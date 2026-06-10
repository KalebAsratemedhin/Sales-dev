import { createApi } from "@reduxjs/toolkit/query/react";
import type { Lead, Persona } from "@/types";
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
    createLead: builder.mutation<
      Lead,
      Partial<Pick<Lead, "email" | "name" | "company_name" | "company_website" | "source" | "profile_url" | "persona">>
    >({
      query: (body) => ({
        url: "/",
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "Leads", id: "LIST" }],
    }),
    getPersonas: builder.query<Persona[], void>({
      query: () => "/personas/",
      transformResponse: (response: Persona[] | { results: Persona[] }) =>
        Array.isArray(response) ? response : response.results,
    }),
    createPersona: builder.mutation<Persona, Partial<Persona>>({
      query: (body) => ({ url: "/personas/", method: "POST", body }),
    }),
    updatePersona: builder.mutation<Persona, { id: number; body: Partial<Persona> }>({
      query: ({ id, body }) => ({ url: `/personas/${id}/`, method: "PATCH", body }),
    }),
    deletePersona: builder.mutation<void, number>({
      query: (id) => ({ url: `/personas/${id}/`, method: "DELETE" }),
    }),
    sendOutreach: builder.mutation<{ queued: boolean }, number>({
      query: (leadId) => ({
        url: `/${leadId}/send-outreach/`,
        method: "POST",
      }),
      invalidatesTags: (_r, _e, leadId) => [
        { type: "Lead", id: leadId },
        { type: "Leads", id: "LIST" },
      ],
    }),
  }),
});

export const {
  useGetLeadsQuery,
  useGetLeadQuery,
  useCreateLeadMutation,
  useGetPersonasQuery,
  useCreatePersonaMutation,
  useUpdatePersonaMutation,
  useDeletePersonaMutation,
  useSendOutreachMutation,
} = leadsApi;
