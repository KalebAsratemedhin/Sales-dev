import { createApi } from "@reduxjs/toolkit/query/react";
import type {
  ActivityLogLine,
  EmailThreadDetail,
  EmailThreadSummary,
  GoogleAuthUrl,
  GoogleStatus,
  OutreachStats,
  PaginatedResponse,
  ScheduledMeeting,
} from "@/types";
import { getApiBase } from "@/lib/apiBase";
import { createBaseQueryWithReauth } from "@/lib/baseQueryWithReauth";

const base = getApiBase();
const baseUrl = base ? `${base}/api/outreach` : "/api/outreach";

export const outreachApi = createApi({
  reducerPath: "outreachApi",
  baseQuery: createBaseQueryWithReauth(baseUrl),
  tagTypes: ["Threads", "Thread", "OutreachStats", "Google", "Meetings", "Activity"],
  endpoints: (builder) => ({
    getStats: builder.query<OutreachStats, void>({
      query: () => "/stats/",
      providesTags: ["OutreachStats"],
    }),
    getMeetings: builder.query<
      PaginatedResponse<ScheduledMeeting>,
      { when?: "upcoming" | "past" | "all"; page?: number; page_size?: number } | void
    >({
      query: (arg) => ({
        url: "/meetings/",
        params: {
          ...(arg?.when ? { when: arg.when } : {}),
          ...(arg?.page ? { page: String(arg.page) } : {}),
          ...(arg?.page_size ? { page_size: String(arg.page_size) } : {}),
        },
      }),
      providesTags: ["Meetings"],
    }),
    getActivity: builder.query<
      PaginatedResponse<ActivityLogLine>,
      { page?: number; page_size?: number } | void
    >({
      query: (arg) => ({
        url: "/activity/",
        params: {
          ...(arg?.page ? { page: String(arg.page) } : {}),
          ...(arg?.page_size ? { page_size: String(arg.page_size) } : {}),
        },
      }),
      providesTags: ["Activity"],
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
        "Activity",
      ],
    }),
    getGoogleStatus: builder.query<GoogleStatus, void>({
      query: () => "/google/status/",
      providesTags: ["Google"],
    }),
    getGoogleAuthUrl: builder.query<GoogleAuthUrl, void>({
      query: () => "/google/auth-url/",
    }),
    exchangeGoogleCode: builder.mutation<GoogleStatus, { code: string; state: string }>({
      query: (body) => ({
        url: "/google/exchange/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Google"],
    }),
    disconnectGoogle: builder.mutation<GoogleStatus, void>({
      query: () => ({
        url: "/google/disconnect/",
        method: "POST",
      }),
      invalidatesTags: ["Google"],
    }),
    updateGoogleSettings: builder.mutation<
      GoogleStatus,
      Partial<Pick<GoogleStatus, "calendar_id" | "timezone" | "meeting_duration_minutes">>
    >({
      query: (body) => ({
        url: "/google/settings/",
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["Google"],
    }),
    syncGoogleN8n: builder.mutation<GoogleStatus, void>({
      query: () => ({
        url: "/google/sync-n8n/",
        method: "POST",
      }),
      invalidatesTags: ["Google"],
    }),
  }),
});

export const {
  useGetStatsQuery,
  useGetMeetingsQuery,
  useGetActivityQuery,
  useGetThreadsQuery,
  useGetThreadQuery,
  useDraftReplyMutation,
  useSendReplyMutation,
  useGetGoogleStatusQuery,
  useLazyGetGoogleAuthUrlQuery,
  useExchangeGoogleCodeMutation,
  useDisconnectGoogleMutation,
  useUpdateGoogleSettingsMutation,
  useSyncGoogleN8nMutation,
} = outreachApi;
