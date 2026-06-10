"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { toast } from "@/components/ui/use-toast";
import {
  useCreatePersonaMutation,
  useDeletePersonaMutation,
  useGetPersonasQuery,
} from "@/store/leadsApi";

export function PersonaManager() {
  const { data: personas = [], refetch } = useGetPersonasQuery();
  const [createPersona, { isLoading: creating }] = useCreatePersonaMutation();
  const [deletePersona] = useDeletePersonaMutation();
  const [name, setName] = useState("");

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    try {
      await createPersona({ name: name.trim(), is_active: true }).unwrap();
      setName("");
      refetch();
      toast({ title: "Persona created" });
    } catch {
      toast({ title: "Failed to create persona", variant: "destructive" });
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deletePersona(id).unwrap();
      refetch();
      toast({ title: "Persona deleted" });
    } catch {
      toast({ title: "Delete failed", variant: "destructive" });
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2 text-primary font-bold text-xs tracking-wider uppercase">
          <span className="material-symbols-outlined text-sm">groups</span>
          <span>Personas</span>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={handleCreate} className="flex gap-2 items-end">
          <div className="flex-1">
            <Label htmlFor="personaName">New persona</Label>
            <Input id="personaName" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <Button type="submit" disabled={creating}>
            Add
          </Button>
        </form>
        {personas.length === 0 ? (
          <p className="text-slate-500 text-sm">No personas yet.</p>
        ) : (
          <ul className="divide-y divide-primary/10">
            {personas.map((p) => (
              <li key={p.id} className="py-2 flex items-center justify-between gap-2">
                <span className="text-slate-100 text-sm font-medium">{p.name}</span>
                <Button variant="ghost" onClick={() => handleDelete(p.id)} className="text-red-400 text-xs">
                  Delete
                </Button>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
