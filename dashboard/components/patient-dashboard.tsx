"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

type Patient = {
  patient_id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string | null;
  sex: string | null;
  phone_number: string | null;
  email: string | null;
  address_line_1: string | null;
  address_line_2: string | null;
  city: string | null;
  state: string | null;
  zip_code: string | null;
  insurance_provider: string | null;
  insurance_member_id: string | null;
  preferred_language: string | null;
  emergency_contact_name: string | null;
  emergency_contact_phone: string | null;
  created_at: string | null;
  updated_at: string | null;
  deleted_at: string | null;
};

type ApiEnvelope<T> = {
  data: T | null;
  error: string | null;
};

type Filters = {
  last_name: string;
  phone_number: string;
  date_of_birth: string;
};

const defaultFilters: Filters = {
  last_name: "",
  phone_number: "",
  date_of_birth: "",
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "https://voice-ai-patient-registration-ua8y.onrender.com";

const formatDate = (value: string | null | undefined) => {
  if (!value) return "—";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
};

const formatPhone = (value: string | null | undefined) => {
  if (!value) return "—";
  const digits = value.replace(/\D/g, "");
  if (digits.length !== 10) return value;
  return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
};

const formatName = (patient: Patient) =>
  [patient.first_name, patient.last_name].filter(Boolean).join(" ") || "Unknown patient";

const getValue = (value: string | null | undefined) => {
  if (value === null || value === undefined || value === "") return "—";
  return value;
};

const fetchPatients = async (filters: Filters): Promise<Patient[]> => {
  const params = new URLSearchParams();

  if (filters.last_name.trim()) {
    params.set("last_name", filters.last_name.trim());
  }

  if (filters.phone_number.trim()) {
    params.set("phone_number", filters.phone_number.trim());
  }

  if (filters.date_of_birth) {
    params.set("date_of_birth", filters.date_of_birth);
  }

  const url = `${API_BASE_URL}/patients${params.size > 0 ? `?${params.toString()}` : ""}`;
  const response = await fetch(url, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
    cache: "no-store",
  });

  const body = (await response.json().catch(() => ({}))) as Partial<ApiEnvelope<Patient[]>>;

  if (!response.ok) {
    throw new Error(
      body?.error ??
        body?.data?.toString?.() ??
        `Request failed with status ${response.status}`,
    );
  }

  if (body?.error) {
    throw new Error(String(body.error));
  }

  if (!Array.isArray(body?.data)) {
    return [];
  }

  return body.data as Patient[];
};

export function PatientDashboard() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasActiveFilters = useMemo(
    () => Object.values(filters).some((value) => value.trim().length > 0),
    [filters],
  );

  const loadPatients = useCallback(
    async (nextFilters: Filters, refresh = false) => {
      if (refresh) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }

      setError(null);

      try {
        const result = await fetchPatients(nextFilters);
        setPatients(result);
      } catch (caughtError) {
        const message =
          caughtError instanceof Error
            ? caughtError.message
            : "Failed to load patients. Please try again.";
        setPatients([]);
        setError(message);
      } finally {
        setIsLoading(false);
        setIsRefreshing(false);
      }
    },
    [],
  );

  useEffect(() => {
    void loadPatients(defaultFilters);
  }, [loadPatients]);

  const handleFilterChange = (field: keyof Filters, value: string) => {
    setFilters((current) => ({ ...current, [field]: value }));
  };

  const handleSearch = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await loadPatients(filters);
  };

  const handleReset = async () => {
    setFilters(defaultFilters);
    await loadPatients(defaultFilters);
  };

  const handleRefresh = async () => {
    await loadPatients(filters, true);
  };

  const detailFields = selectedPatient
    ? [
        ["Patient ID", selectedPatient.patient_id],
        ["Full Name", formatName(selectedPatient)],
        ["Date of Birth", formatDate(selectedPatient.date_of_birth)],
        ["Sex", getValue(selectedPatient.sex)],
        ["Phone", formatPhone(selectedPatient.phone_number)],
        ["Email", getValue(selectedPatient.email)],
        ["Address Line 1", getValue(selectedPatient.address_line_1)],
        ["Address Line 2", getValue(selectedPatient.address_line_2)],
        ["City", getValue(selectedPatient.city)],
        ["State", getValue(selectedPatient.state)],
        ["ZIP", getValue(selectedPatient.zip_code)],
        ["Insurance Provider", getValue(selectedPatient.insurance_provider)],
        ["Insurance Member ID", getValue(selectedPatient.insurance_member_id)],
        ["Preferred Language", getValue(selectedPatient.preferred_language)],
        ["Emergency Contact", getValue(selectedPatient.emergency_contact_name)],
        ["Emergency Contact Phone", formatPhone(selectedPatient.emergency_contact_phone)],
        ["Registration Date", formatDate(selectedPatient.created_at)],
        ["Last Updated", formatDate(selectedPatient.updated_at)],
      ]
    : [];

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <header className="border-b border-slate-200 bg-white/90 backdrop-blur-sm">
        <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-sky-600 text-lg font-bold text-white shadow-sm">
                C
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-700">
                  CareCloud
                </p>
                <h1 className="text-2xl font-semibold text-slate-900">
                  Patient Registration Dashboard
                </h1>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-right">
                <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-700">
                  Total Registered
                </div>
                <div className="text-2xl font-bold text-emerald-900">{patients.length}</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <section className="mb-6 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 bg-slate-50 px-4 py-4 sm:px-6">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">Patient search</h2>
                <p className="text-sm text-slate-600">
                  Search by last name, phone number, or date of birth.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={handleRefresh}
                  disabled={isRefreshing}
                  className="inline-flex items-center justify-center rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isRefreshing ? "Refreshing..." : "Refresh"}
                </button>
              </div>
            </div>
          </div>

          <form onSubmit={handleSearch} className="space-y-4 p-4 sm:p-6">
            <div className="grid gap-4 md:grid-cols-3">
              <label className="block">
                <span className="mb-1.5 block text-sm font-medium text-slate-700">Last name</span>
                <input
                  type="text"
                  value={filters.last_name}
                  onChange={(event) => handleFilterChange("last_name", event.target.value)}
                  placeholder="Smith"
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
                />
              </label>

              <label className="block">
                <span className="mb-1.5 block text-sm font-medium text-slate-700">Phone number</span>
                <input
                  type="tel"
                  value={filters.phone_number}
                  onChange={(event) => handleFilterChange("phone_number", event.target.value)}
                  placeholder="5551234567"
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
                />
              </label>

              <label className="block">
                <span className="mb-1.5 block text-sm font-medium text-slate-700">Date of birth</span>
                <input
                  type="date"
                  value={filters.date_of_birth}
                  onChange={(event) => handleFilterChange("date_of_birth", event.target.value)}
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
                />
              </label>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <button
                type="submit"
                className="inline-flex items-center justify-center rounded-lg bg-sky-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-sky-500"
              >
                Search patients
              </button>

              <button
                type="button"
                onClick={handleReset}
                className="inline-flex items-center justify-center rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:bg-slate-50"
              >
                Clear
              </button>

              {hasActiveFilters ? (
                <span className="text-sm text-slate-600">
                  Showing filtered results for {patients.length} patient{patients.length === 1 ? "" : "s"}.
                </span>
              ) : null}
            </div>
          </form>
        </section>

        {error ? (
          <div className="mb-6 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
            <strong className="font-semibold">Unable to load patients.</strong> {error}
          </div>
        ) : null}

        <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-3 sm:px-6">
            <h2 className="text-base font-semibold text-slate-900">Registered patients</h2>
            <span className="rounded-full bg-sky-100 px-2.5 py-1 text-xs font-medium text-sky-700">
              {patients.length} total
            </span>
          </div>

          {isLoading ? (
            <div className="flex min-h-[240px] items-center justify-center">
              <div className="flex items-center gap-3 text-slate-600">
                <span className="inline-flex h-5 w-5 animate-spin rounded-full border-2 border-sky-200 border-t-sky-600" />
                Loading patients...
              </div>
            </div>
          ) : patients.length === 0 ? (
            <div className="flex min-h-[240px] items-center justify-center px-6 text-center">
              <div>
                <div className="mb-3 text-4xl">📋</div>
                <h3 className="text-lg font-semibold text-slate-900">No patients match these filters</h3>
                <p className="mt-2 text-sm text-slate-600">
                  Try clearing the search fields or checking a different phone number or date of birth.
                </p>
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm text-slate-700">
                <thead className="bg-slate-50 text-slate-700">
                  <tr>
                    {[
                      "Patient ID",
                      "Full Name",
                      "Date of Birth",
                      "Sex",
                      "Phone",
                      "City",
                      "State",
                      "ZIP",
                      "Registration Date",
                    ].map((column) => (
                      <th
                        key={column}
                        className="border-b border-slate-200 px-4 py-3 font-semibold whitespace-nowrap"
                      >
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {patients.map((patient) => (
                    <tr
                      key={patient.patient_id}
                      onClick={() => setSelectedPatient(patient)}
                      className="cursor-pointer border-b border-slate-200 transition hover:bg-sky-50/60"
                    >
                      <td className="px-4 py-3 font-medium text-slate-900 whitespace-nowrap">
                        {patient.patient_id}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">{formatName(patient)}</td>
                      <td className="px-4 py-3 whitespace-nowrap">{formatDate(patient.date_of_birth)}</td>
                      <td className="px-4 py-3 whitespace-nowrap">{getValue(patient.sex)}</td>
                      <td className="px-4 py-3 whitespace-nowrap">{formatPhone(patient.phone_number)}</td>
                      <td className="px-4 py-3 whitespace-nowrap">{getValue(patient.city)}</td>
                      <td className="px-4 py-3 whitespace-nowrap">{getValue(patient.state)}</td>
                      <td className="px-4 py-3 whitespace-nowrap">{getValue(patient.zip_code)}</td>
                      <td className="px-4 py-3 whitespace-nowrap">{formatDate(patient.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>

      {selectedPatient ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm">
          <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-2xl bg-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 sm:px-6">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-sky-700">
                  Patient profile
                </p>
                <h3 className="mt-1 text-xl font-semibold text-slate-900">{formatName(selectedPatient)}</h3>
              </div>
              <button
                type="button"
                onClick={() => setSelectedPatient(null)}
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
              >
                Close
              </button>
            </div>

            <div className="grid gap-4 p-5 sm:grid-cols-2 sm:p-6">
              {detailFields.map(([label, value]) => (
                <div key={label} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                  <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                    {label}
                  </dt>
                  <dd className="mt-2 text-sm font-medium text-slate-900">{value}</dd>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
