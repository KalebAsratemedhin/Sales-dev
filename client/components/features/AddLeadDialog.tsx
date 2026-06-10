"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { toast } from "@/components/ui/use-toast";
import { useCreateLeadMutation, useGetPersonasQuery } from "@/store/leadsApi";

export function AddLeadDialog() {
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [companyWebsite, setCompanyWebsite] = useState("");
  const [personaId, setPersonaId] = useState<string>("");

  const [createLead, { isLoading }] = useCreateLeadMutation();
  const { data: personas = [] } = useGetPersonasQuery(undefined, { skip: !open });

  const reset = () => {
    setEmail("");
    setName("");
    setCompanyName("");
    setCompanyWebsite("");
    setPersonaId("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) {
      toast({ title: "Email required", variant: "destructive" });
      return;
    }
    try {
      await createLead({
        email: email.trim(),
        name: name.trim(),
        company_name: companyName.trim(),
        company_website: companyWebsite.trim(),
        source: "csv",
        persona: personaId ? Number(personaId) : null,
      }).unwrap();
      toast({ title: "Lead created", description: companyWebsite.trim() ? "Research enqueued." : undefined });
      reset();
      setOpen(false);
    } catch {
      toast({ title: "Failed to create lead", variant: "destructive" });
    }
  };

  if (!open) {
    return (
      <Button onClick={() => setOpen(true)} className="gap-2">
        <span className="material-symbols-outlined text-sm">add</span>
        Add Lead
      </Button>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md bg-background border border-primary/20 rounded-xl p-6 space-y-4"
      >
        <h2 className="text-lg font-bold text-slate-100">Add Lead</h2>
        <div>
          <Label htmlFor="lead-email">Email *</Label>
          <Input id="lead-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <div>
          <Label htmlFor="lead-name">Name</Label>
          <Input id="lead-name" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div>
          <Label htmlFor="lead-company">Company</Label>
          <Input id="lead-company" value={companyName} onChange={(e) => setCompanyName(e.target.value)} />
        </div>
        <div>
          <Label htmlFor="lead-website">Company website</Label>
          <Input
            id="lead-website"
            type="url"
            placeholder="https://"
            value={companyWebsite}
            onChange={(e) => setCompanyWebsite(e.target.value)}
          />
        </div>
        {personas.length > 0 && (
          <div>
            <Label htmlFor="lead-persona">Persona</Label>
            <select
              id="lead-persona"
              value={personaId}
              onChange={(e) => setPersonaId(e.target.value)}
              className="w-full rounded-md border border-primary/20 bg-primary/5 px-3 py-2 text-sm text-slate-100"
            >
              <option value="">None</option>
              {personas.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
        )}
        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Creating…" : "Create"}
          </Button>
        </div>
      </form>
    </div>
  );
}
