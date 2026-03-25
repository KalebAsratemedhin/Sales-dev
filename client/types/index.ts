export interface OutreachConfig {
  linkedin_url: string;
  calendly_scheduling_url: string;
  product_docs_path: string;
  chroma_collection_name: string;
  updated_at: string;
}

export interface UserProfile {
  full_name: string;
  email: string;
  profile_pic_url?: string | null;
}

export interface UserSettings {
  linkedin_profile_url: string;
  calendly_scheduling_url: string;
  linkedin_last_sync?: string | null;
}

export interface ProductDoc {
  id: number;
  filename: string;
  uploaded_at: string;
}

export interface ProductDocListResponse {
  items: ProductDoc[];
}

export interface Lead {
  id: number;
  email: string;
  name: string;
  company_name: string;
  company_website: string;
  source: string;
  profile_url: string;
  persona: number | null;
  status: string;
  created_at: string;
  updated_at: string;
}

/** For when Research API is exposed (list jobs, get by lead). */
export interface Research {
  id: number;
  lead_id: number;
  website_summary?: string;
  pain_points?: string[];
  created_at: string;
}

/** For when Outreach/Inbox thread API is exposed. */
export interface EmailThread {
  id: number;
  lead_id: number;
  subject?: string;
  last_message_at: string;
}

export interface SentEmail {
  id: number;
  thread_id: number;
  direction: "outbound" | "inbound";
  body?: string;
  sent_at: string;
}
