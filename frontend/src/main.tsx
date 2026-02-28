import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import App from "./App";
import { useWebSocket } from "./hooks/useWebSocket";
import "./index.css";

const queryClient = new QueryClient();

function AppWithWebSocket() {
  useWebSocket();
  return <App />;
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <Toaster position="top-right" />
        <AppWithWebSocket />
      </QueryClientProvider>
    </BrowserRouter>
  </React.StrictMode>
);

