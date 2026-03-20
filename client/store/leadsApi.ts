import { createApi } from "@reduxjs/toolkit/query/react";
import type { Lead } from "@/types";
import { getApiBase } from "@/lib/apiBase";
import { createBaseQueryWithReauth } from "@/lib/baseQueryWithReauth";

const base = getApiBase();
const baseUrl = base ? `${base}/api/leads` : "/api/leads";

export const leadsApi = createApi({
  reducerPath: "leadsApi",
  baseQuery: createBaseQueryWithReauth(baseUrl),
  tagTypes: ["Leads", "Lead"],
  endpoints: (builder) => ({
    getLeads: builder.query<Lead[], { status?: string } | void>({
      query: (arg) => {
        const params = arg?.status ? { status: arg.status } : undefined;
        return { url: "/", params };
      },
      transformResponse: (response: Lead[] | { results: Lead[] }) =>
        Array.isArray(response) ? response : response.results,
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: "Lead" as const, id })),
              { type: "Leads", id: "LIST" },
            ]
          : [{ type: "Leads", id: "LIST" }],
    }),
    getLead: builder.query<Lead, number>({
      query: (id) => `/${id}/`,
      providesTags: (_result, _err, id) => [{ type: "Lead", id }],
    }),
  }),
});

export const { useGetLeadsQuery, useGetLeadQuery } = leadsApi;
