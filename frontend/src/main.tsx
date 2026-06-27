import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./App";
import { RoleProvider } from "./role";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: { queries: { refetchOnWindowFocus: false, retry: 1 } },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter basename={(import.meta as any).env?.VITE_ROUTER_BASE || "/"}>
        <RoleProvider>
          <App />
        </RoleProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
