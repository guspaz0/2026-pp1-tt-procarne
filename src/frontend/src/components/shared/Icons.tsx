/**
 * Iconos SVG del diseño Figma "ROCCA - Control Cadena Cárnica SDE - /".
 * Todos usan currentColor para heredar el color del texto/contenedor.
 */
import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement> & { size?: number };

const base = (size: number | undefined, props: IconProps) => ({
  width: size ?? 16,
  height: size ?? 16,
  viewBox: "0 0 16 16",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.3,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  ...props,
});

/** Wifi / interconexión federal */
export function IconWifi({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)}>
      <path d="M1.5 5.5a10 10 0 0 1 13 0" />
      <path d="M3.5 8a7 7 0 0 1 9 0" />
      <path d="M5.5 10.5a4 4 0 0 1 5 0" />
      <circle cx="8" cy="13" r="0.8" fill="currentColor" stroke="none" />
    </svg>
  );
}

/** Módulo IV: Monitor Estratégico — gráfico de barras */
export function IconChart({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)}>
      <path d="M2 14V8" />
      <path d="M6 14V4" />
      <path d="M10 14V6" />
      <path d="M14 14V2" />
    </svg>
  );
}

/** Módulo I: Operadores — usuario */
export function IconUser({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)}>
      <circle cx="8" cy="5" r="2.6" />
      <path d="M3 14a5 5 0 0 1 10 0" />
    </svg>
  );
}

/** Módulos II & VII: Remitos REC — documento */
export function IconDoc({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)}>
      <rect x="3" y="1.5" width="10" height="13" rx="1.5" />
      <path d="M5.5 5h5" />
      <path d="M5.5 8h5" />
      <path d="M5.5 11h3" />
    </svg>
  );
}

/** Módulo III: Fiscalización en Ruta — camión */
export function IconTruck({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)}>
      <path d="M1.5 3.5h8v7h-8z" />
      <path d="M9.5 6h3l2 2.5v2h-5" />
      <circle cx="4.5" cy="12.5" r="1.3" />
      <circle cx="11.5" cy="12.5" r="1.3" />
    </svg>
  );
}

/** Módulo VI: Faena en Origen — planta / molino */
export function IconFactory({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)}>
      <path d="M2 14V6l4 2.5V6l4 2.5V4h4v10z" />
    </svg>
  );
}

/** Módulo V: Portal Público — globo */
export function IconGlobe({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)}>
      <circle cx="8" cy="8" r="6" />
      <path d="M2 8h12" />
      <path d="M8 2c2 1.8 3 3.8 3 6s-1 4.2-3 6c-2-1.8-3-3.8-3-6s1-4.2 3-6z" />
    </svg>
  );
}

/** Cámara / ver cartón original */
export function IconCamera({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)}>
      <rect x="1.5" y="4" width="13" height="9" rx="1.5" />
      <circle cx="8" cy="8.5" r="2.5" />
      <path d="M5.5 4 6.5 2h3L10.5 4" />
    </svg>
  );
}

/** Descargar / exportar CSV */
export function IconDownload({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)}>
      <path d="M8 2v8" />
      <path d="M4.5 7 8 10.5 11.5 7" />
      <path d="M2.5 13.5h11" />
    </svg>
  );
}

/** Padrón de sucursales — edificios */
export function IconBuildings({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)}>
      <rect x="2" y="5" width="5" height="9" />
      <rect x="9" y="2" width="5" height="12" />
      <path d="M3.5 7.5h2M3.5 10h2M10.5 4.5h2M10.5 7h2M10.5 9.5h2" />
    </svg>
  );
}

/** Jerarquía — diagrama de árbol */
export function IconHierarchy({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)}>
      <rect x="5.5" y="1.5" width="5" height="4" rx="1" />
      <rect x="1" y="10.5" width="4" height="4" rx="1" />
      <rect x="11" y="10.5" width="4" height="4" rx="1" />
      <path d="M8 5.5v3M3 10.5V8.5h10v2" />
    </svg>
  );
}

/** Formulario — lápiz en hoja */
export function IconForm({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)}>
      <rect x="2" y="1.5" width="12" height="13" rx="1.5" />
      <path d="M5 5h6M5 8h6M5 11h3" />
    </svg>
  );
}

/** Escudo / sello oficial */
export function IconShield({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)}>
      <path d="M8 1.5 13 3.5v4c0 3.5-2.2 5.8-5 7-2.8-1.2-5-3.5-5-7v-4z" />
      <path d="M5.5 8 7.2 9.7 10.5 6.3" />
    </svg>
  );
}

/** Cargar datos — flecha hacia arriba en bandeja */
export function IconUpload({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)}>
      <path d="M8 10V2.5" />
      <path d="M4.5 6 8 2.5 11.5 6" />
      <path d="M2.5 10v3.5h11V10" />
    </svg>
  );
}

/** Check para checkbox (fill) */
export function IconCheck(props: IconProps) {
  return (
    <svg viewBox="0 0 14 14" width={14} height={14} fill="none" {...props}>
      <path
        d="M3 7.5 6 10.5 11 4"
        stroke="currentColor"
        strokeWidth={1.75}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/** Chevron down para dropdowns */
export function IconChevronDown({ size, ...props }: IconProps) {
  return (
    <svg {...base(size, props)} viewBox="0 0 10 6">
      <path d="M1 1l4 4 4-4" />
    </svg>
  );
}

// [AGROTRAZA] desactivado
// /** Sello AGROTRAZA — hoja */
// export function IconLeaf({ size, ...props }: IconProps) {
//   return (
//     <svg {...base(size, props)}>
//       <path d="M13 3C8 3 4.5 5.5 4 10c0 0 0 2.5 0 2.5S4 14 6.5 14c4.5-.5 7-4 7-9V3z" />
//       <path d="M4 12.5C6 9 9 6.5 12 4.5" />
//     </svg>
//   );
// }
