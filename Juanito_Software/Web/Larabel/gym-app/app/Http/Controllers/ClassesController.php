<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Classe;
use Illuminate\Validation\Rule;

class ClassesController extends Controller
{
    public function index()
    {   
        if (auth()->user()->role === 'coach') {
            return redirect()->route('coach.classes.index');
        }

        $classes = Classe::all();
        return view('classes.index', compact('classes'));
    }

    public function create()
    {
        $coaches = \App\Models\Coach::all();
        return view('classes.create', compact('coaches'));
    }


    public function store(Request $request)
    {
        try {
            $request->merge([
                'init_hour' => $request->filled('init_hour') ? substr((string) $request->input('init_hour'), 0, 5) : $request->input('init_hour'),
                'final_hour' => $request->filled('final_hour') ? substr((string) $request->input('final_hour'), 0, 5) : $request->input('final_hour'),
            ]);

            $validated = $request->validate([
                'name'        => 'required|string|max:100|unique:classes,name',
                'desc'        => 'nullable|string|max:255',
                'coach_id'    => 'required|exists:coaches,id',
                'days'        => 'required|string|max:100',
                'init_hour'   => 'required|date_format:H:i',
                'final_hour'  => 'required|date_format:H:i|after:init_hour',
            ], [
                'name.required' => 'El nombre de la clase es obligatorio.',
                'name.unique' => 'Ya existe una clase con ese nombre.',
                'coach_id.required' => 'Debe seleccionar un entrenador.',
                'coach_id.exists' => 'El entrenador seleccionado no existe.',
                'days.required' => 'Los días de la semana son obligatorios.',
                'init_hour.required' => 'La hora de inicio es obligatoria.',
                'init_hour.date_format' => 'La hora de inicio debe tener el formato HH:MM.',
                'final_hour.required' => 'La hora de fin es obligatoria.',
                'final_hour.date_format' => 'La hora de fin debe tener el formato HH:MM.',
                'final_hour.after' => 'La hora de fin debe ser posterior a la hora de inicio.',
            ]);

            // Asegurar que desc sea null si está vacío
            if (empty($validated['desc'])) {
                $validated['desc'] = null;
            }

            Classe::create($validated);
            
            // Solo admin puede crear clases (protegido por middleware)
            return redirect()->route('admin.classes.index')->with('success', 'Clase creada correctamente');
            
        } catch (\Illuminate\Validation\ValidationException $e) {
            return back()->withErrors($e->errors())->withInput();
        } catch (\Exception $e) {
            \Log::error('Error al crear clase: ' . $e->getMessage());
            return back()->withErrors(['error' => 'Error al crear la clase. Por favor, inténtalo de nuevo.'])->withInput();
        }
    }

    public function show(Classe $class)
    {
        if (auth()->user()->role === 'coach') {

            $coach = auth()->user()->coach;

            if (!$coach || $class->coach_id !== $coach->id) {
                abort(403, 'No tienes acceso a esta clase');
            }
        }

        return view('classes.show', compact('class'));
    }



    public function edit($id)
    {
        $class = Classe::findOrFail($id);
        $coaches = \App\Models\Coach::all();
        return view('classes.edit', compact('class', 'coaches'));
    }


    public function update(Request $request, $id)
    {
        $class = Classe::findOrFail($id);

        $request->merge([
            'init_hour' => $request->filled('init_hour') ? substr((string) $request->input('init_hour'), 0, 5) : $request->input('init_hour'),
            'final_hour' => $request->filled('final_hour') ? substr((string) $request->input('final_hour'), 0, 5) : $request->input('final_hour'),
        ]);

        $validated = $request->validate([
            'name'        => ['required', 'string', 'max:100', Rule::unique('classes', 'name')->ignore($class->id)],
            'desc'        => 'nullable|string|max:255',
            'coach_id'    => 'required|exists:coaches,id',
            'days'        => 'required|string|max:100',
            'init_hour'   => 'required|date_format:H:i',
            'final_hour'  => 'required|date_format:H:i|after:init_hour',
        ], [
            'name.required' => 'El nombre de la clase es obligatorio.',
            'coach_id.required' => 'Debe seleccionar un entrenador.',
            'coach_id.exists' => 'El entrenador seleccionado no existe.',
            'days.required' => 'Los días de la semana son obligatorios.',
            'init_hour.required' => 'La hora de inicio es obligatoria.',
            'init_hour.date_format' => 'La hora de inicio debe tener el formato HH:MM.',
            'final_hour.required' => 'La hora de fin es obligatoria.',
            'final_hour.date_format' => 'La hora de fin debe tener el formato HH:MM.',
            'final_hour.after' => 'La hora de fin debe ser posterior a la hora de inicio.',
        ]);

        $class->update($validated);
        
        // Solo admin puede editar clases (protegido por middleware)
        return redirect()->route('admin.classes.index')->with('success', 'Clase actualizada correctamente');
    }

    public function destroy($id)
    {
        Classe::findOrFail($id)->delete();
        
        // Solo admin puede eliminar clases (protegido por middleware)
        return redirect()->route('admin.classes.index')->with('success', 'Clase eliminada correctamente');
    }

    public function myClasses()
    {
        $coach = auth()->user()->coach;

        if (!$coach) {
            return redirect()
                ->route('dashboard')
                ->with('error', 'No se encontró información de entrenador.');
        }

        $classes = Classe::where('coach_id', $coach->id)
            ->withCount('inscriptions')
            ->get();

        return view('classes.my-classes', compact('classes'));
    }

}
