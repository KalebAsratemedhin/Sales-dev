import { createApi } from "@reduxjs/toolkit/query/react";
import type {
  EmailThreadDetail,
  EmailThreadSummary,
  GmailAuthUrl,
  GmailStatus,
  GoogleCalendarAuthUrl,
  GoogleCalendarStatus,
  OutreachStats,
} from "@/types";
import { getApiBase } from "@/lib/apiBase";
import { createBaseQueryWithReauth } from "@/lib/baseQueryWithReauth";

const base = getApiBase();
const baseUrl = base ? `${base}/api/outreach` : "/api/outreach";

export const outreachApi = createApi({
  reducerPath: "outreachApi",
  baseQuery: createBaseQueryWithReauth(baseUrl),
  tagTypes: ["Threads", "Thread", "OutreachStats", "Calendar", "Gmail"],
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
    getCalendarStatus: builder.query<GoogleCalendarStatus, void>({
      query: () => "/calendar/status/",
      providesTags: ["Calendar"],
    }),
    getCalendarAuthUrl: builder.query<GoogleCalendarAuthUrl, void>({
      query: () => "/calendar/auth-url/",
    }),
    exchangeCalendarCode: builder.mutation<GoogleCalendarStatus, { code: string; state: string }>({
      query: (body) => ({
        url: "/calendar/exchange/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Calendar"],
    }),
    disconnectCalendar: builder.mutation<{ connected: boolean; oauth_app_configured: boolean }, void>({
      query: () => ({
        url: "/calendar/disconnect/",
        method: "POST",
      }),
      invalidatesTags: ["Calendar"],
    }),
    updateCalendarSettings: builder.mutation<
      GoogleCalendarStatus,
      Partial<Pick<GoogleCalendarStatus, "calendar_id" | "timezone" | "meeting_duration_minutes">>
    >({
      query: (body) => ({
        url: "/calendar/settings/",
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["Calendar"],
    }),
    getGmailStatus: builder.query<GmailStatus, void>({
      query: () => "/gmail/status/",
      providesTags: ["Gmail"],
    }),
    getGmailAuthUrl: builder.query<GmailAuthUrl, void>({
      query: () => "/gmail/auth-url/",
    }),
    exchangeGmailCode: builder.mutation<GmailStatus, { code: string; state: string }>({
      query: (body) => ({
        url: "/gmail/exchange/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Gmail"],
    }),
    disconnectGmail: builder.mutation<GmailStatus, void>({
      query: () => ({
        url: "/gmail/disconnect/",
        method: "POST",
      }),
      invalidatesTags: ["Gmail"],
    }),
    syncGmailN8n: builder.mutation<GmailStatus, void>({
      query: () => ({
        url: "/gmail/sync-n8n/",
        method: "POST",
      }),
      invalidatesTags: ["Gmail"],
    }),
  }),
});

export const {
  useGetStatsQuery,
  useGetThreadsQuery,
  useGetThreadQuery,
  useDraftReplyMutation,
  useSendReplyMutation,
  useGetCalendarStatusQuery,
  useLazyGetCalendarAuthUrlQuery,
  useExchangeCalendarCodeMutation,
  useDisconnectCalendarMutation,
  useUpdateCalendarSettingsMutation,
  useGetGmailStatusQuery,
  useLazyGetGmailAuthUrlQuery,
  useExchangeGmailCodeMutation,
  useDisconnectGmailMutation,
  useSyncGmailN8nMutation,
} = outreachApi;
