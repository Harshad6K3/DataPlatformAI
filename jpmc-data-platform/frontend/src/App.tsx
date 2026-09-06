import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthProvider";
import { ProtectedRoute } from "./auth/ProtectedRoute";
import { MetricCard } from "./components/MetricCard";
import { PageHeader } from "./components/PageHeader";
import { StatusBadge } from "./components/StatusBadge";

const queryClient = new QueryClient();
const services = [["Catalog", "active"], ["Governance", "active"], ["Lineage", "warning"], ["Pipeline agent", "active"], ["Recon agent", "inactive"]] as const;

function Dashboard() {
  return <div className="min-h-screen bg-surface"><PageHeader title="Data Platform Overview" breadcrumbs={["Home", "Dashboard"]} /><main className="mx-auto max-w-7xl px-6 py-8 md:px-10"><section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"><MetricCard label="Datasets governed" value="1,284" trend="+8.4% this month" trendUp /><MetricCard label="Active pipelines" value="42" trend="+3 from last week" trendUp /><MetricCard label="Data quality score" value="98.2%" trend="Within target" trendUp /><MetricCard label="Open incidents" value="3" trend="-2 this week" trendUp /></section><section className="mt-8 border border-border bg-white p-6 shadow-sm"><div className="flex items-center justify-between border-b border-border pb-4"><h2 className="font-semibold text-navy">Service health</h2><span className="font-mono text-xs text-slate-500">Updated just now</span></div><div className="grid gap-5 pt-5 sm:grid-cols-2 lg:grid-cols-5">{services.map(([name, status]) => <div className="flex items-center justify-between gap-3" key={name}><span className="text-sm text-slate-700">{name}</span><StatusBadge status={status} /></div>)}</div></section></main></div>;
}

function Login() {
  return <main className="flex min-h-screen items-center justify-center bg-navy p-6"><div className="w-full max-w-md border border-slate-700 bg-white p-8"><p className="font-mono text-xs font-semibold uppercase tracking-widest text-accent">JPMC AI Data Platform</p><h1 className="mt-4 text-2xl font-semibold text-navy">Sign in to continue</h1><Link className="mt-8 block bg-accent px-4 py-3 text-center text-sm font-semibold text-white" to="/">Continue with SSO</Link></div></main>;
}

export default function App() {
  return <QueryClientProvider client={queryClient}><AuthProvider><BrowserRouter><Routes><Route path="/login" element={<Login />} /><Route element={<ProtectedRoute />}><Route path="/" element={<Dashboard />} /></Route></Routes></BrowserRouter></AuthProvider></QueryClientProvider>;
}