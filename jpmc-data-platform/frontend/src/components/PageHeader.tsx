import type { ReactNode } from "react";

export function PageHeader({ title, breadcrumbs, actions }: { title: string; breadcrumbs?: string[]; actions?: ReactNode }) {
  return <header className="border-b-4 border-accent bg-navy px-6 py-6 text-white md:px-10"><div className="mx-auto flex max-w-7xl items-end justify-between gap-4"><div><nav className="mb-3 text-xs text-slate-300">{breadcrumbs?.join(" / ")}</nav><h1 className="text-2xl font-semibold tracking-tight">{title}</h1></div>{actions}</div></header>;
}