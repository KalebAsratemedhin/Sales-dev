import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { OutreachConfig } from "@/types";
import { getApiBase } from "@/lib/apiBase";

const base = getApiBase();
const baseUrl = base ? `${base}/api/outreach` : "/api/outreach";

export const outreachConfigApi = createApi({
  reducerPath: "outreachConfigApi",
  baseQuery: fetchBaseQuery({
    baseUrl: baseUrl ? `${baseUrl}/api/outreach` : "/api/outreach",
    prepareHeaders: (headers) => {
      headers.set("Content-Type", "application/json");
      return headers;
    },
  }),
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
