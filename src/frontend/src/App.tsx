import { BrowserRouter } from "react-router-dom";
import { AppRoutes } from "./AppRoutes";
import { ToastContainer } from "./components/shared/ToastContainer";

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
      <ToastContainer />
    </BrowserRouter>
  );
}

export default App;
