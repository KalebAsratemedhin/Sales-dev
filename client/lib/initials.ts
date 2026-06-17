export function initials(name: string, email: string): string {
  const trimmed = name?.trim() ?? "";
  if (trimmed) {
    const parts = trimmed.split(/\s+/);
    if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    if (parts[0].length >= 2) return parts[0].slice(0, 2).toUpperCase();
    return parts[0][0].toUpperCase();
  }
  if (email?.length >= 2) return email.slice(0, 2).toUpperCase();
  return "—";
}
