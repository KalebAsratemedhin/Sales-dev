import { createApi } from "@reduxjs/toolkit/query/react";
import { getApiBase } from "@/lib/apiBase";
import { createBaseQueryWithReauth } from "@/lib/baseQueryWithReauth";
import { leadsApi } from "./leadsApi";

const base = getApiBase();
const baseUrl = base ? `${base}/api/linkedin` : "/api/linkedin";

export type LinkedInSyncCounts = { created: number; updated: number };

export const linkedinApi = createApi({
  reducerPath: "linkedinApi",
  baseQuery: createBaseQueryWithReauth(baseUrl),
  endpoints: (builder) => ({
    syncFromPosts: builder.mutation<
      LinkedInSyncCounts,
      { post_urls: string[]; persona_id?: number | null }
    >({
      query: (body) => ({
        url: "/sync/posts/",
        method: "POST",
        body,
      }),
      async onQueryStarted(_arg, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled;
          dispatch(leadsApi.util.invalidateTags([{ type: "Leads", id: "LIST" }]));
        } catch {
          /* ignore */
        }
      },
    }),
    syncFromProfile: builder.mutation<
      LinkedInSyncCounts,
      {
        profile_url: string;
        start_date: string;
        end_date: string;
        persona_id?: number | null;
        max_scrolls?: number;
      }
    >({
      query: (body) => ({
        url: "/sync/profile/",
        method: "POST",
        body,
      }),
      async onQueryStarted(_arg, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled;
          dispatch(leadsApi.util.invalidateTags([{ type: "Leads", id: "LIST" }]));
        } catch {
          /* ignore */
        }
      },
    }),
  }),
});

export const { useSyncFromPostsMutation, useSyncFromProfileMutation } = linkedinApi;
