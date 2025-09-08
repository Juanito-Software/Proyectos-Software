# hotkey_manager.py  (reemplaza la clase anterior por esta)
import ctypes
from ctypes import wintypes
import time
import threading
import queue

class HotkeyManager:
    # Modifiers
    MOD_ALT     = 0x0001
    MOD_CONTROL = 0x0002
    MOD_SHIFT   = 0x0004
    MOD_WIN     = 0x0008

    WM_HOTKEY = 0x0312
    WM_USER   = 0x0400

    def __init__(self, app):
        self.app = app
        self.user32 = ctypes.windll.user32
        self._next_id = 1
        self._registered = {}    # hid -> (mod, vk, callback, debounce_ms)
        self._pending = []       # items to register in the msg thread: (hid, mod, vk, callback, debounce_ms)
        self._running = False
        self._msg_thread = None
        self._last_trigger = {}  # hid -> last_time_ms
        self._lock = threading.Lock()

    def _next_hotkey_id(self):
        with self._lock:
            hid = self._next_id
            self._next_id += 1
            return hid

    def register_hotkey(self, modifier, vk, callback, debounce_ms=50):
        """
        Register a hotkey. You can call this before or after hk.start().
        Returns the hotkey id (hid).
        """
        hid = self._next_hotkey_id()
        entry = (hid, modifier, vk, callback, debounce_ms)

        with self._lock:
            # Add to pending list; message thread will perform the RegisterHotKey call
            self._pending.append(entry)

        # Wake the message thread if it's already running
        if self._msg_thread and self._msg_thread.ident:
            try:
                # Post a benign message to wake the thread to process pending
                self.user32.PostThreadMessageW(self._msg_thread.ident, self.WM_USER, 0, 0)
            except Exception:
                pass

        return hid

    def unregister_hotkey(self, hid):
        with self._lock:
            # If registered already, ask the message thread to unregister it immediately
            if hid in self._registered:
                try:
                    self.user32.UnregisterHotKey(None, hid)
                except Exception:
                    pass
                self._registered.pop(hid, None)
            else:
                # If it was still pending, remove it from pending
                self._pending = [p for p in self._pending if p[0] != hid]

    def start(self):
        if self._running:
            return
        self._running = True
        self._msg_thread = threading.Thread(target=self._message_loop, daemon=True)
        self._msg_thread.start()

    def stop(self):
        self._running = False
        # wake thread
        try:
            if self._msg_thread and self._msg_thread.ident:
                self.user32.PostThreadMessageW(self._msg_thread.ident, 0x0012, 0, 0)  # WM_QUIT
        except Exception:
            pass

        # Unregister all (best-effort)
        with self._lock:
            for hid in list(self._registered.keys()):
                try:
                    self.user32.UnregisterHotKey(None, hid)
                except Exception:
                    pass
            self._registered.clear()
            self._pending.clear()

    def _message_loop(self):
        # Bring local references
        PeekMessage = self.user32.PeekMessageW
        TranslateMessage = self.user32.TranslateMessage
        DispatchMessage = self.user32.DispatchMessageW
        msg = wintypes.MSG()
        PM_REMOVE = 0x0001

        def process_pending():
            # register any pending hotkeys from main thread - MUST be called from this thread
            with self._lock:
                pending = list(self._pending)
                self._pending.clear()
            for hid, mod, vk, cb, db in pending:
                success = False
                try:
                    success = bool(self.user32.RegisterHotKey(None, hid, mod, vk))
                except Exception:
                    success = False
                if success:
                    with self._lock:
                        self._registered[hid] = (mod, vk, cb, db)
                else:
                    # couldn't register (already in use?). Keep it unregistered but store callback so user can try again later.
                    # Optionally log:
                    print(f"[HotkeyManager] warning: RegisterHotKey failed for id={hid}, mod={mod}, vk={vk}")

        # initial pending processing
        process_pending()

        while self._running:
            # process newly pending registrations
            process_pending()

            has = PeekMessage(ctypes.byref(msg), None, 0, 0, PM_REMOVE)
            if not has:
                # no message: small sleep to avoid busy loop
                time.sleep(0.01)
                continue

            # process message
            if msg.message == self.WM_HOTKEY:
                hid = msg.wParam
                now = time.time() * 1000
                with self._lock:
                    entry = self._registered.get(hid)
                if entry:
                    mod, vk, callback, debounce_ms = entry
                    last = self._last_trigger.get(hid, 0)
                    if now - last >= debounce_ms:
                        self._last_trigger[hid] = now
                        # schedule callback in Tk thread
                        try:
                            # callback might be any callable; schedule wrapped call for safety
                            self.app.root.after(0, lambda cb=callback: cb())
                        except Exception as e:
                            print("Error scheduling hotkey callback:", e)

            # always translate/dispatch
            try:
                TranslateMessage(ctypes.byref(msg))
                DispatchMessage(ctypes.byref(msg))
            except Exception:
                pass

        # cleanup: unregister any registered hotkeys
        with self._lock:
            for hid in list(self._registered.keys()):
                try:
                    self.user32.UnregisterHotKey(None, hid)
                except Exception:
                    pass
            self._registered.clear()
