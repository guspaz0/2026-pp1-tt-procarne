/**
 * Layout base de la aplicación ROCCA: Header + NavBar + contenido + Footer.
 * Se usa como shell común para todos los módulos.
 */
import type { ReactNode } from "react";
import { Footer } from "./Footer";
import { Header } from "./Header";
import { NavBar } from "./NavBar";

export function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-rocca-fondo">
      <Header />
      <NavBar />
      <main className="mx-auto w-full max-w-[1280px] flex-1 px-4 py-5">
        <div className="overflow-hidden rounded-xl border border-rocca-borde bg-white shadow-[0_1px_2px_rgba(0,0,0,0.05)]">
          {children}
        </div>
      </main>
      <Footer />
    </div>
  );
}
