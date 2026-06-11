import { Toaster as SonnerToaster } from 'sonner';

export function Toaster() {
  return (
    <SonnerToaster
      position="top-right"
      richColors
      theme="dark"
      toastOptions={{
        style: {
          background: 'rgba(18, 18, 30, 0.95)',
          border: '1px solid rgba(124, 58, 237, 0.15)',
          backdropFilter: 'blur(20px)',
          color: '#e2e2f0',
        },
      }}
    />
  );
}
