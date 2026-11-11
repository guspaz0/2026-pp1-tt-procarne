import { configureStore, combineReducers } from "@reduxjs/toolkit";
import authReducer from "./authSlice";
import operadoresReducer from "./operadoresSlice";
import formF102Reducer from "./formF102Slice";
import { operadoresApi } from "./api";

/**
 * Root reducer combinado. Se separa de la creación del store para poder
 * inyectar `preloadedState` en tests (component tests + Node).
 */
const rootReducer = combineReducers({
  auth: authReducer,
  operadores: operadoresReducer,
  formF102: formF102Reducer,
  [operadoresApi.reducerPath]: operadoresApi.reducer,
});

export type RootState = ReturnType<typeof rootReducer>;
export type AppDispatch = ReturnType<
  typeof setupStore
>['dispatch'];

/**
 * Crea una instancia de store. En la app usamos el singleton `store`; en
 * tests llamamos a `setupStore()` para obtener una instancia FRESCA por
 * test (evita que el cache de RTK Query de un test se filtre al siguiente).
 *
 * `preloadedState` permite sembrar slices (p. ej. `formF102`) antes de montar.
 */
export function setupStore(preloadedState?: Partial<RootState>) {
  return configureStore({
    reducer: rootReducer,
    preloadedState: preloadedState as never,
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(operadoresApi.middleware),
    devTools: true,
  });
}

/** Store global de la aplicación ROCCA (singleton). */
export const store = setupStore();
