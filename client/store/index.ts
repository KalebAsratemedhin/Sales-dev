import { configureStore } from "@reduxjs/toolkit";
import { leadsApi } from "./leadsApi";
import { outreachConfigApi } from "./outreachConfigApi";
import { authApi } from "./authApi";

export const makeStore = () =>
  configureStore({
    reducer: {
      [outreachConfigApi.reducerPath]: outreachConfigApi.reducer,
      [leadsApi.reducerPath]: leadsApi.reducer,
      [authApi.reducerPath]: authApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(
        outreachConfigApi.middleware,
        leadsApi.middleware,
        authApi.middleware
      ),
  });

export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore["getState"]>;
export type AppDispatch = AppStore["dispatch"];
