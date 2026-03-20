"use client";

import * as React from "react";
import * as ToastPrimitives from "@radix-ui/react-toast";
import { dismiss, subscribe, type ToastState } from "./use-toast";
import { Toast, ToastClose, ToastDescription, ToastTitle, ToastViewport } from "./toast";

export function Toaster() {
  const [toasts, setToasts] = React.useState<ToastState[]>([]);

  React.useEffect(() => {
    return subscribe(setToasts);
  }, []);

  return (
    <ToastPrimitives.Provider>
      {toasts.map(({ id, title, description, variant, durationMs }) => (
        <Toast
          key={id}
          variant={variant}
          open={true}
          duration={durationMs}
          onOpenChange={(open) => {
            if (!open) dismiss(id);
          }}
        >
          <div className="flex-1">
            <ToastTitle>{title}</ToastTitle>
            {description ? <ToastDescription>{description}</ToastDescription> : null}
          </div>
          <ToastClose />
        </Toast>
      ))}
      <ToastViewport />
    </ToastPrimitives.Provider>
  );
}

