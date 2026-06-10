import { createApi } from "@reduxjs/toolkit/query/react";
import type { Research, ResearchListItem, ResearchStats } from "@/types";
import { getApiBase } from "@/lib/apiBase";
import { createBaseQueryWithReauth } from "@/lib/baseQueryWithReauth";

const base = getApiBase();
const baseUrl = base ? `${base}/api/research` : "/api/research";

export const researchApi = createApi({
  reducerPath: "researchApi",
  baseQuery: createBaseQueryWithReauth(baseUrl),
  tagTypes: ["Research", "ResearchStats"],
  endpoints: (builder) => ({
    getStats: builder.query<ResearchStats, void>({
      query: () => "/stats/",
      providesTags: ["ResearchStats"],
    }),
    getResearchList: builder.query<ResearchListItem[], void>({
      query: () => "/",
      providesTags: ["Research"],
    }),
    getResearchByLead: builder.query<Research, number>({
      query: (leadId) => `/leads/${leadId}/`,
      providesTags: (_r, _e, leadId) => [{ type: "Research", id: leadId }],
    }),
  }),
});

export const { useGetStatsQuery, useGetResearchListQuery, useGetResearchByLeadQuery } = researchApi;
