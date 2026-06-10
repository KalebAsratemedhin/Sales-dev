import { configureStore } from "@reduxjs/toolkit";
import { leadsApi } from "./leadsApi";
import { outreachApi } from "./outreachApi";
import { outreachConfigApi } from "./outreachConfigApi";
import { researchApi } from "./researchApi";
import { authApi } from "./authApi";

export const makeStore = () =>
  configureStore({
    reducer: {
      [outreachConfigApi.reducerPath]: outreachConfigApi.reducer,
      [outreachApi.reducerPath]: outreachApi.reducer,
      [researchApi.reducerPath]: researchApi.reducer,
      [leadsApi.reducerPath]: leadsApi.reducer,
      [authApi.reducerPath]: authApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(
        outreachConfigApi.middleware,
        outreachApi.middleware,
        researchApi.middleware,
        leadsApi.middleware,
        authApi.middleware
      ),
  });

export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore["getState"]>;
export type AppDispatch = AppStore["dispatch"];
