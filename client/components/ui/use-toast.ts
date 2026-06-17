export type ToastVariant = "default" | "destructive";

export type ToastOptions = {
  id?: string;
  title: string;
  description?: string;
  variant?: ToastVariant;
  durationMs?: number;
};

const MAX_TOASTS = 3;

export type ToastState = ToastOptions & {
  id: string;
  durationMs: number;
};

type Listener = (toasts: ToastState[]) => void;

let toasts: ToastState[] = [];
const listeners = new Set<Listener>();

function notify() {
  for (const listener of listeners) listener(toasts);
}

function makeId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function subscribe(listener: Listener) {
  listeners.add(listener);
  listener(toasts);
  return () => {
    listeners.delete(listener);
  };
}

export function dismiss(id: string) {
  toasts = toasts.filter((t) => t.id !== id);
  notify();
}

export function toast(options: ToastOptions) {
  const id = options.id ?? makeId();
  const durationMs = options.durationMs ?? 5000;

  const nextToast: ToastState = {
    id,
    title: options.title,
    description: options.description,
    variant: options.variant ?? "default",
    durationMs,
  };

  toasts = [...toasts.filter((t) => t.id !== id), nextToast].slice(-MAX_TOASTS);
  notify();

  if (typeof window !== "undefined") {
    window.setTimeout(() => {
      dismiss(id);
    }, durationMs);
  }

  return id;
}

