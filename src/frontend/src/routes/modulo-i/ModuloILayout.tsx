/**
 * Layout del Módulo I: AppLayout + PageHeader + Tabs + contenido.
 * El contenido (tab activo) se pasa por `children`.
 */
import type { ReactNode } from "react";
import { AppLayout } from "../../components/layout/AppLayout";
import { ModuloITabs } from "./ModuloITabs";
import { PageHeader } from "./PageHeader";

type ModuloILayoutProps = {
  children: ReactNode;
  onVerCarton?: () => void;
};

export function ModuloILayout({
  children,
  onVerCarton,
}: ModuloILayoutProps) {
  return (
    <AppLayout>
      <PageHeader onVerCarton={onVerCarton} />
      <ModuloITabs />
      {children}
    </AppLayout>
  );
}
