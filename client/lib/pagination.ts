export const DEFAULT_PAGE_SIZE = 10;

export function paginate<T>(items: T[], page: number, pageSize: number = DEFAULT_PAGE_SIZE) {
  const total = items.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const currentPage = Math.min(Math.max(1, page), totalPages);
  const start = (currentPage - 1) * pageSize;

  return {
    items: items.slice(start, start + pageSize),
    total,
    totalPages,
    currentPage,
    pageSize,
    from: total === 0 ? 0 : start + 1,
    to: Math.min(start + pageSize, total),
  };
}
