/**
 * Layout para las rutas de operador: Header + contenido + Footer.
 * Sin NavBar (por el momento el operador no usa la barra de módulos).
 */
import type { ReactNode } from "react";
import { Footer } from "../../components/layout/Footer";
import { Header } from "../../components/layout/Header";

export function OperadorLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-rocca-fondo">
      <Header />
      <main className="mx-auto w-full max-w-[1280px] flex-1 px-4 py-5">
        <div className="overflow-hidden rounded-xl border border-rocca-borde bg-white shadow-[0_1px_2px_rgba(0,0,0,0.05)]">
          {children}
        </div>
      </main>
      <Footer />
    </div>
  );
}
