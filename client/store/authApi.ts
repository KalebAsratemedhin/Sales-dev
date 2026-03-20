import { createApi } from "@reduxjs/toolkit/query/react";
import { getApiBase } from "@/lib/apiBase";
import { createBaseQueryWithReauth } from "@/lib/baseQueryWithReauth";
import type { ProductDocListResponse, UserProfile, UserSettings } from "@/types";

export type AuthTokens = { access: string; refresh?: string };
export type MeResponse = { full_name: string; email: string };

const base = getApiBase();
const baseUrl = base ? `${base}/api/auth` : "/api/auth";

export const authApi = createApi({
  reducerPath: "authApi",
  baseQuery: createBaseQueryWithReauth(baseUrl),
  tagTypes: ["Profile", "Settings", "ProductDocs"],
  endpoints: (builder) => ({
    register: builder.mutation<AuthTokens, { full_name: string; email: string; password: string }>({
      query: (body) => ({
        url: "/register/",
        method: "POST",
        body,
      }),
    }),
    login: builder.mutation<AuthTokens, { email: string; password: string }>({
      query: (body) => ({
        url: "/login/",
        method: "POST",
        body,
      }),
    }),
    refresh: builder.mutation<AuthTokens, { refresh: string }>({
      query: (body) => ({
        url: "/refresh/",
        method: "POST",
        body,
      }),
    }),
    me: builder.query<MeResponse, void>({
      query: () => ({
        url: "/me/",
        method: "GET",
      }),
      providesTags: ["Profile"],
    }),

    getProfile: builder.query<UserProfile, void>({
      query: () => ({ url: "/profile/", method: "GET" }),
      providesTags: ["Profile"],
    }),

    updateProfile: builder.mutation<UserProfile, FormData>({
      query: (formData) => ({
        url: "/profile/",
        method: "PATCH",
        body: formData,
      }),
      invalidatesTags: ["Profile"],
    }),

    getSettings: builder.query<UserSettings, void>({
      query: () => ({ url: "/settings/", method: "GET" }),
      providesTags: ["Settings"],
    }),

    updateSettings: builder.mutation<UserSettings, Partial<UserSettings>>({
      query: (body) => ({
        url: "/settings/",
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["Settings"],
    }),

    getProductDocs: builder.query<ProductDocListResponse, void>({
      query: () => ({ url: "/product-docs/", method: "GET" }),
      providesTags: ["ProductDocs"],
    }),

    getProfilePic: builder.query<Blob, void>({
      query: () => ({ url: "/profile/pic/", method: "GET" }),
    }),

    getProductDocFile: builder.query<Blob, number>({
      query: (docId) => ({ url: `/product-docs/${docId}/`, method: "GET" }),
    }),

    uploadProductDocs: builder.mutation<
      { uploaded: { id: number; filename: string }[] },
      FormData
    >({
      query: (formData) => ({
        url: "/product-docs/",
        method: "POST",
        body: formData,
      }),
      invalidatesTags: ["ProductDocs"],
    }),
  }),
});

export const {
  useRegisterMutation,
  useLoginMutation,
  useRefreshMutation,
  useMeQuery,
  useGetProfileQuery,
  useUpdateProfileMutation,
  useGetSettingsQuery,
  useUpdateSettingsMutation,
  useGetProductDocsQuery,
  useLazyGetProductDocFileQuery,
  useGetProfilePicQuery,
  useUploadProductDocsMutation,
} = authApi;

