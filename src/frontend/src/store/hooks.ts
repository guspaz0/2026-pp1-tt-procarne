import { useDispatch, useSelector } from "react-redux";
import type { TypedUseSelectorHook } from "react-redux";
import type { AppDispatch, RootState } from "./store";

/**
 * Hooks tipados para el store.
 * Uso: `const dispatch = useAppDispatch(); const busqueda = useAppSelector((s) => s.operadores.busqueda);`
 */
export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
