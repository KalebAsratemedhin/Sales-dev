import { createApi } from "@reduxjs/toolkit/query/react";
import type { OutreachConfig } from "@/types";
import { getApiBase } from "@/lib/apiBase";
import { createBaseQueryWithReauth } from "@/lib/baseQueryWithReauth";

const base = getApiBase();
const baseUrl = base ? `${base}/api/outreach` : "/api/outreach";

export const outreachConfigApi = createApi({
  reducerPath: "outreachConfigApi",
  baseQuery: createBaseQueryWithReauth(baseUrl),
  tagTypes: ["Config"],
  endpoints: (builder) => ({
    getConfig: builder.query<OutreachConfig, void>({
      query: () => "/config/",
      providesTags: ["Config"],
    }),
    updateConfig: builder.mutation<
      OutreachConfig,
      Partial<Pick<OutreachConfig, "linkedin_url" | "calendly_scheduling_url" | "product_docs_path" | "chroma_collection_name">>
    >({
      query: (body) => ({
        url: "/config/",
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["Config"],
    }),
  }),
});

export const { useGetConfigQuery, useUpdateConfigMutation } = outreachConfigApi;
