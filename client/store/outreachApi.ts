import { createApi } from "@reduxjs/toolkit/query/react";
import type { EmailThreadDetail, EmailThreadSummary, OutreachStats } from "@/types";
import { getApiBase } from "@/lib/apiBase";
import { createBaseQueryWithReauth } from "@/lib/baseQueryWithReauth";

const base = getApiBase();
const baseUrl = base ? `${base}/api/outreach` : "/api/outreach";

export const outreachApi = createApi({
  reducerPath: "outreachApi",
  baseQuery: createBaseQueryWithReauth(baseUrl),
  tagTypes: ["Threads", "Thread", "OutreachStats"],
  endpoints: (builder) => ({
    getStats: builder.query<OutreachStats, void>({
      query: () => "/stats/",
      providesTags: ["OutreachStats"],
    }),
    getThreads: builder.query<EmailThreadSummary[], { filter?: string; lead_id?: number } | void>({
      query: (arg) => {
        const params: Record<string, string> = {};
        if (arg?.filter) params.filter = arg.filter;
        if (arg?.lead_id) params.lead_id = String(arg.lead_id);
        return { url: "/threads/", params: Object.keys(params).length ? params : undefined };
      },
      providesTags: ["Threads"],
    }),
    getThread: builder.query<EmailThreadDetail, number>({
      query: (id) => `/threads/${id}/`,
      providesTags: (_r, _e, id) => [{ type: "Thread", id }],
    }),
    draftReply: builder.mutation<{ body: string }, number>({
      query: (threadId) => ({
        url: `/threads/${threadId}/draft/`,
        method: "POST",
      }),
    }),
    sendReply: builder.mutation<{ sent: boolean }, { threadId: number; body: string }>({
      query: ({ threadId, body }) => ({
        url: `/threads/${threadId}/send/`,
        method: "POST",
        body: { body },
      }),
      invalidatesTags: (_r, _e, { threadId }) => [
        { type: "Thread", id: threadId },
        "Threads",
        "OutreachStats",
      ],
    }),
  }),
});

export const {
  useGetStatsQuery,
  useGetThreadsQuery,
  useGetThreadQuery,
  useDraftReplyMutation,
  useSendReplyMutation,
} = outreachApi;
