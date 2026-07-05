import { AuthProvider, useAuth } from "./AuthContext";
import AuthPage from "./AuthPage";
import TasksPage from "./TasksPage";

function Router() {
  const { token } = useAuth();
  return token ? <TasksPage /> : <AuthPage />;
}

export default function App() {
  return (
    <AuthProvider>
      <Router />
    </AuthProvider>
  );
}
