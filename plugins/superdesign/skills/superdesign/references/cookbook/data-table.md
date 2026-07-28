# Data table (sortable, filterable, dense)

> A keyboard-first, dense-but-calm data table built on the industry-standard
> **headless engine + presentational shell** architecture: [TanStack Table v8]
> owns the logic (sort, filter, facet, select, paginate), [shadcn/ui] `Table`
> primitives render semantic `<table>` markup, and Radix popovers/menus drive the
> toolbar. This is the pattern Linear, Stripe, and Vercel ship.

- **Stack:** React 19 + Tailwind v4 + shadcn/ui (new-york) + TanStack Table v8
- **Slug:** `data-table`
- **Complexity:** High — but the 3-file split keeps each file small and reusable.

---

## 1. When to use it

Reach for this recipe when users need to **scan, compare, sort, and act on many
structured records** — issues, invoices, users, deployments, transactions.

| Use a data table when… | Use something else when… |
|---|---|
| Rows share a schema and columns are comparable across rows | Each record is a rich document → use cards or a detail page |
| Users sort/filter/select/bulk-act | You show ≤ a handful of key/value pairs → use a description list |
| Density and scan-ability matter (finance, ops, admin) | The data is a hierarchy or nested tree → use a tree/outline view |
| Rows are auditable and referenceable ("row 42", "invoice #INV-203") | The primary interaction is a single continuous feed → use a virtualized list |

**Sizing the engine to the data:**

- **≤ ~1,000 rows in memory** → client-side (TanStack does sort/filter/paginate). This recipe's default.
- **> ~1,000 rows or live data** → server-side: flip on `manualSorting / manualFiltering / manualPagination`, sync state to the URL, and refetch. Same components, different data source.
- **Tens of thousands of rows in one continuous list** → add [TanStack Virtual] (windowed body, sticky header). Do **not** make the table engine the scroll container.

---

## 2. Anatomy

Five canonical regions, top → bottom:

```
┌─────────────────────────────────────────────────────────────────────┐
│  TOOLBAR                                                             │  ← global search · faceted filters · active-filter chips + Reset
│  [ Search… ]  [Status ▾] [Priority ▾]  ·  Reset ✕      [View ▾] [+]  │    · View (column visibility) · density · primary action
├───┬──────────────┬────────────┬──────────┬────────────┬─────────────┤
│ ☐ │ TASK ▲       │ TITLE      │ STATUS   │ PRIORITY   │        [⋯]   │  ← HEADER: select-all · sort chevron · aria-sort
├───┼──────────────┼────────────┼──────────┼────────────┼─────────────┤
│ ☐ │ TASK-8782    │ Convert…   │ ● In prog│ ↑ High     │        [⋯]   │  ← BODY rows: checkbox (hover/focus-revealed) ·
│ ☐ │ TASK-7878    │ Try to…    │ ○ Backlog│ → Medium   │        [⋯]   │    typed cells · row actions kebab
├───┴──────────────┴────────────┴──────────┴────────────┴─────────────┤
│  0 of 100 row(s) selected.        Rows/page [25 ▾]  ‹ Page 1/4 › »   │  ← FOOTER: selection count · rows-per-page · page controls
└─────────────────────────────────────────────────────────────────────┘
    ▲ sticky header on vertical scroll · freeze identity (first) + actions (last) column on horizontal scroll
    ▲ on selection: a bottom-fixed BULK-ACTION BAR slides in
```

1. **Toolbar** — global search (debounced), faceted filter popovers, active-filter chips + "Reset", column-visibility ("View") menu, optional density switcher, primary action (Add/Import/Export).
2. **Header row** — column titles, sort affordance (chevron that never shifts text alignment), select-all checkbox, optional resize handles on separator hover.
3. **Body** — rows → cells. Row-level: checkbox (revealed on hover/focus), typed cells, hover/focus-revealed `⋯` actions menu, optional expand chevron.
4. **Footer / pagination** — "X of Y selected", rows-per-page selector, page controls.
5. **Sticky/frozen** — header pins on vertical scroll; first (identity) + last (actions) columns can freeze on horizontal scroll.

**Cell building blocks:** text, numeric (tabular + right-aligned), badge/status, avatar+name, date, truncated-with-tooltip, editable.

---

## 3. Token-driven styling

Every color comes from a **shadcn CSS variable** (`--background`, `--muted`,
`--border`, `--ring`, `--primary`…), consumed through Tailwind utilities
(`bg-background`, `text-muted-foreground`, `border-border`, `ring-ring`). No
hardcoded hex anywhere — the table inherits light/dark and any rebrand for free.

```css
/* app/globals.css — Tailwind v4, @theme inline maps tokens to utilities.
   These are the shadcn defaults you already have; shown for reference. */
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --border: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --radius: 0.625rem;
}
.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --border: oklch(1 0 0 / 10%);
  --ring: oklch(0.556 0 0);
}
```

**The whole visual system in tokens** (this is what makes it read as "calm dense"):

| Concern | Token / utility | Rationale |
|---|---|---|
| Row separator | `border-b border-border` (1px) | One subtle divider, not borders-everywhere |
| Hover row | `hover:bg-muted/50` | ~50% muted so it never fights selection |
| Selected row | `data-[state=selected]:bg-muted` | Persistent, stronger than hover |
| Keyboard focus | `focus-visible:ring-2 ring-ring ring-offset-2 ring-offset-background` | Never rely on hover alone |
| Header text | `text-muted-foreground font-medium` | Recedes; content leads |
| Muted/secondary text | `text-muted-foreground` | IDs, timestamps, counts |
| Numeric cells | `tabular-nums text-right` | Aligned digits; scan for outliers |

> **Density is not a hardcoded pixel value — it's a variable.** Drive row height
> from a single CSS custom property so a switcher can change all rows at once:

```css
@layer components {
  [data-density="compact"]     { --row-h: 2.25rem; --cell-py: 0.375rem; } /* ~40px */
  [data-density="comfortable"] { --row-h: 3rem;    --cell-py: 0.75rem;  } /* ~48px */
  [data-density="spacious"]    { --row-h: 3.5rem;  --cell-py: 1rem;     } /* ~56px */
}
```

Cells then use `style={{ paddingBlock: 'var(--cell-py)' }}` and rows
`style={{ height: 'var(--row-h)' }}`, so density is one attribute on the wrapper.

---

## 4. Variants

### Variant A — Client-side faceted table (this recipe's default)

Everything in memory. TanStack does sort/filter/paginate/facet. Toolbar has global
search + faceted multi-select popovers (Status, Priority) with **live counts** from
`getFacetedUniqueValues()`. Best for ≤ ~1,000 rows. This is the shadcn "tasks"
pattern and what the code below implements.

### Variant B — Server-side, URL-synced table

Same components, but state lives in the URL query string and drives a fetch:

```tsx
// The only structural change: manual flags + state from the URL, data from a query.
const table = useReactTable({
  data,                       // ← from useQuery(['tasks', sorting, filters, page])
  columns,
  rowCount: totalCount,       // ← total from the server, not data.length
  manualSorting: true,
  manualFiltering: true,
  manualPagination: true,
  state: { sorting, columnFilters, pagination },
  onSortingChange: setSorting,        // setters write to URL (nuqs / searchParams)
  onColumnFiltersChange: setColumnFilters,
  onPaginationChange: setPagination,
  getCoreRowModel: getCoreRowModel(), // ← no getSorted/Filtered/Pagination row models
})
```

URL-synced state is what every best-in-class fork (openstatus, tablecn,
shadcn-admin) does: views become shareable, refresh-safe, and back-button-safe.
For very large or real-time sets, swap offset pagination for **cursor/keyset**
(Stripe's `starting_after` / `ending_before`) to avoid page-number drift.

---

## 5. Interaction / state matrix

Design **every** one of these — the empty and error states are where slop shows.

| State | Treatment |
|---|---|
| **Default row** | Quiet 1px bottom border (`border-b`), no fill. |
| **Hover row** | `hover:bg-muted/50`; reveals checkbox + `⋯` actions. |
| **Focus (keyboard)** | Visible focus ring (`focus-visible:ring-2 ring-ring`). Never hover-only. |
| **Selected row** | Persistent tint (`data-[state=selected]:bg-muted`) + checked box; footer count updates. |
| **Disabled row** | `text-muted-foreground`, `pointer-events-none`, no hover. |
| **Editing cell** | Input in place at fixed height (no layout jump); commit on Enter/blur, cancel on Esc. |
| **Sorted column** | Active chevron (▲/▼) + `aria-sort`; multi-sort shows an order index badge. Chevron must not shift header text alignment. |
| **Loading (first load)** | Skeleton the **first ~5 rows**, keep the header + sort icons visible. Never a full-table centered spinner. |
| **Empty — first run** | Illustration/message + primary CTA ("Create your first task"). |
| **Empty — no results** | "No results found." + "Clear filters" (copy distinct from first-run). |
| **Error** | Inline "There was an error loading the data." + Retry; keep the header. |
| **Partial / refetch** | Keep old rows (stale-while-revalidate), dim body or show a top progress bar. |

> Skeletons cut perceived load time up to ~67% vs spinners — but only skeleton the
> first few rows, not the whole set, and **keep the header live**.

---

## 6. Responsive behavior

- **Wrap the table in a horizontal scroll container** (`overflow-x-auto`) with a
  `min-w` so columns never crush below legibility. This is the primitive default.
- **Freeze identity (first) + actions (last) columns** on horizontal scroll via
  column pinning (`position: sticky; left/right: 0` on pinned cells) so users keep
  context while scrolling wide tables.
- **Toolbar collapses:** on narrow viewports, faceted filters fold into a single
  "Filters" popover/sheet; the "View" and density menus stay in an overflow menu.
- **Row height bumps to Spacious on touch** so hit targets clear the 24×24 CSS px
  WCAG 2.2 floor (aim for ~44–48px). Hover-revealed affordances must have a
  persistent equivalent on touch — never hover-only.
- **Below ~640px**, consider swapping the table for a **stacked card list** (label:
  value pairs per record). Tables are fundamentally 2-D; don't force one into a
  phone.
- **Pagination** stacks: rows-per-page selector above page controls.

---

## 7. Accessibility

- **Semantic markup.** shadcn `Table` renders a real `<table>`/`<thead>`/`<tbody>`.
  Keep it — don't rebuild with `<div role="grid">` unless you also implement the
  full grid keyboard model.
- **`aria-sort`** on the active sortable `<th>` (`ascending` / `descending` /
  `none`), toggled with the sort state. Sort control is a real `<button>` inside
  the header with an accessible label ("Sort by Status").
- **Selection.** Checkboxes are real inputs with labels ("Select row",
  "Select all"). Selected count is announced via an `aria-live="polite"` region.
- **Focus & keyboard.** Every actionable element (sort buttons, checkboxes, kebab
  menus, pagination) is tab-reachable with a visible `focus-visible` ring. Radix
  menus/popovers bring roving focus + Esc-to-close for free.
- **Touch targets** ≥ 24×24 CSS px (WCAG 2.2 Target Size, Minimum). Compact rows
  must still give checkboxes/actions a ≥24px hit area — pad the hit area, not the
  row.
- **State is not color-only.** Status/priority cells pair a color dot/badge with an
  **icon + text label** so meaning survives color-blindness and greyscale.
- **Loading/empty/error** live in an `aria-live` region so async changes are
  announced, not silently swapped.

---

## 8. Anti-slop callout

> These are the tells that separate a shipped-by-Linear table from a generated one.
> Reviewers should reject on any of these:

- ❌ **Hover-only actions/checkboxes** with no keyboard/focus/touch equivalent. The
  single most common a11y failure. Mirror every hover affordance on `focus-within`.
- ❌ **Center-aligned text or numbers.** Kills scan-ability and hides outliers.
  Text left, numbers right + `tabular-nums`, headers match their cells.
- ❌ **Proportional numerals for money/metrics** — `$1,111.11` looks smaller than
  `$999.99`. Always `tabular-nums`.
- ❌ **Zebra striping in an interactive table.** It fights hover/selected/disabled/
  focus tints — you end up with 5 competing greys. Use one subtle divider.
- ❌ **Borders everywhere.** Noise. Let whitespace + a single 1px row divider carry
  structure.
- ❌ **Full-table centered spinner** on load. Skeleton the first ~5 rows, keep the
  header.
- ❌ **One generic empty state** for both first-run and no-results. They need
  different copy and different CTAs ("Create your first…" vs "Clear filters").
- ❌ **Infinite scroll on an auditable table.** No precise navigation, no stable
  reference points, hostile to keyboard/screen-reader users. Paginate or virtualize.
- ❌ **Sort chevrons that shift header alignment** — jitter on every click. Reserve
  space for the icon.
- ❌ **Client-rendering > 1,000 rows** with no virtualization/server paging → scroll
  jank.
- ❌ **Non-persistent density/column/filter prefs** and **no "reset to default"** —
  erodes trust; users re-configure every visit.
- ❌ **Cramming a button into every row.** Reveal actions opportunistically in a
  `⋯` menu.

---

## 9. Complete, copy-pasteable code

The canonical **3-file split** (`columns` / `data-table` / `page`) plus the shared
toolbar, pagination, and column-header sub-components. Uses only shadcn primitives
+ Tailwind + TanStack Table.

### Setup

```bash
npx shadcn@latest add table button checkbox badge input \
  dropdown-menu popover command separator skeleton select
npm i @tanstack/react-table
```

### `types.ts` — the row model

```tsx
export type TaskStatus = "backlog" | "todo" | "in_progress" | "done" | "canceled"
export type TaskPriority = "low" | "medium" | "high"

export type Task = {
  id: string          // "TASK-8782"
  title: string
  status: TaskStatus
  priority: TaskPriority
  estimate: number    // story points — a numeric column
  updatedAt: string   // ISO date
}
```

### `data-table-column-header.tsx` — sortable header with `aria-sort`

```tsx
"use client"

import type { Column } from "@tanstack/react-table"
import { ArrowDown, ArrowUp, ChevronsUpDown, EyeOff } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface DataTableColumnHeaderProps<TData, TValue>
  extends React.HTMLAttributes<HTMLDivElement> {
  column: Column<TData, TValue>
  title: string
}

export function DataTableColumnHeader<TData, TValue>({
  column,
  title,
  className,
}: DataTableColumnHeaderProps<TData, TValue>) {
  // Non-sortable column: plain label, no interactive chrome.
  if (!column.getCanSort()) {
    return <div className={cn(className)}>{title}</div>
  }

  const sorted = column.getIsSorted() // "asc" | "desc" | false

  return (
    <div className={cn("flex items-center gap-1", className)}>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            aria-label={`Sort by ${title}`}
            // -ml-2 so the ghost hit-area aligns the label with static headers.
            className="-ml-2 h-8 data-[state=open]:bg-accent"
          >
            <span>{title}</span>
            {/* Fixed-size icon slot: never shifts the label alignment. */}
            {sorted === "desc" ? (
              <ArrowDown className="ml-1 size-3.5" />
            ) : sorted === "asc" ? (
              <ArrowUp className="ml-1 size-3.5" />
            ) : (
              <ChevronsUpDown className="ml-1 size-3.5 opacity-50" />
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuItem onClick={() => column.toggleSorting(false)}>
            <ArrowUp className="size-3.5 text-muted-foreground" /> Asc
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => column.toggleSorting(true)}>
            <ArrowDown className="size-3.5 text-muted-foreground" /> Desc
          </DropdownMenuItem>
          {column.getCanHide() && (
            <>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => column.toggleVisibility(false)}>
                <EyeOff className="size-3.5 text-muted-foreground" /> Hide
              </DropdownMenuItem>
            </>
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}
```

### `columns.tsx` — the `ColumnDef<Task>[]`

```tsx
"use client"

import type { ColumnDef } from "@tanstack/react-table"
import {
  ArrowRight,
  ArrowUp,
  ArrowDown,
  CheckCircle2,
  Circle,
  CircleOff,
  MoreHorizontal,
  Timer,
} from "lucide-react"

import type { Task, TaskPriority, TaskStatus } from "./types"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { DataTableColumnHeader } from "./data-table-column-header"

// Icon + label pairs: meaning never rides on color alone (a11y).
export const STATUSES: Record<
  TaskStatus,
  { label: string; icon: React.ComponentType<{ className?: string }> }
> = {
  backlog: { label: "Backlog", icon: CircleOff },
  todo: { label: "Todo", icon: Circle },
  in_progress: { label: "In progress", icon: Timer },
  done: { label: "Done", icon: CheckCircle2 },
  canceled: { label: "Canceled", icon: CircleOff },
}

export const PRIORITIES: Record<
  TaskPriority,
  { label: string; icon: React.ComponentType<{ className?: string }> }
> = {
  low: { label: "Low", icon: ArrowDown },
  medium: { label: "Medium", icon: ArrowRight },
  high: { label: "High", icon: ArrowUp },
}

export const columns: ColumnDef<Task>[] = [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && "indeterminate")
        }
        onCheckedChange={(v) => table.toggleAllPageRowsSelected(!!v)}
        aria-label="Select all rows"
        // Larger tap target than the visual box (WCAG 2.2 target size).
        className="translate-y-[2px]"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(v) => row.toggleSelected(!!v)}
        aria-label="Select row"
        className="translate-y-[2px]"
      />
    ),
    enableSorting: false,
    enableHiding: false,
    size: 32,
  },
  {
    accessorKey: "id",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Task" />
    ),
    cell: ({ row }) => (
      <span className="font-mono text-xs text-muted-foreground">
        {row.getValue("id")}
      </span>
    ),
    enableHiding: false,
  },
  {
    accessorKey: "title",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Title" />
    ),
    cell: ({ row }) => (
      // Truncate long titles; full value available via native title tooltip.
      <span
        className="block max-w-[420px] truncate font-medium"
        title={row.getValue("title")}
      >
        {row.getValue("title")}
      </span>
    ),
  },
  {
    accessorKey: "status",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Status" />
    ),
    cell: ({ row }) => {
      const s = STATUSES[row.getValue("status") as TaskStatus]
      const Icon = s.icon
      return (
        <div className="flex items-center gap-2">
          <Icon className="size-4 text-muted-foreground" />
          <span>{s.label}</span>
        </div>
      )
    },
    // Enables faceted filtering + counts for this column.
    filterFn: (row, id, value: string[]) =>
      value.includes(row.getValue(id)),
  },
  {
    accessorKey: "priority",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Priority" />
    ),
    cell: ({ row }) => {
      const p = PRIORITIES[row.getValue("priority") as TaskPriority]
      const Icon = p.icon
      return (
        <Badge variant="outline" className="gap-1 font-normal">
          <Icon className="size-3 text-muted-foreground" />
          {p.label}
        </Badge>
      )
    },
    filterFn: (row, id, value: string[]) =>
      value.includes(row.getValue(id)),
  },
  {
    accessorKey: "estimate",
    // Numeric column: right-align header AND cell, tabular figures.
    header: ({ column }) => (
      <DataTableColumnHeader
        column={column}
        title="Estimate"
        className="justify-end"
      />
    ),
    cell: ({ row }) => (
      <div className="text-right tabular-nums">{row.getValue("estimate")}</div>
    ),
  },
  {
    id: "actions",
    enableSorting: false,
    enableHiding: false,
    size: 40,
    cell: ({ row }) => (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            aria-label={`Open actions for ${row.getValue("id")}`}
            // Revealed on row hover/focus, but always reachable by keyboard.
            className="size-8 opacity-0 focus-visible:opacity-100 group-hover/row:opacity-100 data-[state=open]:opacity-100"
          >
            <MoreHorizontal className="size-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem>Edit</DropdownMenuItem>
          <DropdownMenuItem>Make a copy</DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem
            variant="destructive"
            onSelect={() => {
              /* delete(row.original.id) */
            }}
          >
            Delete
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    ),
  },
]
```

### `data-table-faceted-filter.tsx` — multi-select popover with live counts

```tsx
"use client"

import type { Column } from "@tanstack/react-table"
import { Check, PlusCircle } from "lucide-react"

import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { Separator } from "@/components/ui/separator"

interface Option {
  label: string
  value: string
  icon?: React.ComponentType<{ className?: string }>
}

interface DataTableFacetedFilterProps<TData, TValue> {
  column?: Column<TData, TValue>
  title: string
  options: Option[]
}

export function DataTableFacetedFilter<TData, TValue>({
  column,
  title,
  options,
}: DataTableFacetedFilterProps<TData, TValue>) {
  const facets = column?.getFacetedUniqueValues()
  const selected = new Set(column?.getFilterValue() as string[] | undefined)

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm" className="h-8 border-dashed">
          <PlusCircle className="size-3.5" />
          {title}
          {selected.size > 0 && (
            <>
              <Separator orientation="vertical" className="mx-1 h-4" />
              <Badge
                variant="secondary"
                className="rounded-sm px-1 font-normal lg:hidden"
              >
                {selected.size}
              </Badge>
              <div className="hidden gap-1 lg:flex">
                {selected.size > 2 ? (
                  <Badge variant="secondary" className="rounded-sm px-1 font-normal">
                    {selected.size} selected
                  </Badge>
                ) : (
                  options
                    .filter((o) => selected.has(o.value))
                    .map((o) => (
                      <Badge
                        key={o.value}
                        variant="secondary"
                        className="rounded-sm px-1 font-normal"
                      >
                        {o.label}
                      </Badge>
                    ))
                )}
              </div>
            </>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-52 p-0" align="start">
        <Command>
          <CommandInput placeholder={title} />
          <CommandList>
            <CommandEmpty>No results found.</CommandEmpty>
            <CommandGroup>
              {options.map((option) => {
                const isSelected = selected.has(option.value)
                const Icon = option.icon
                return (
                  <CommandItem
                    key={option.value}
                    onSelect={() => {
                      if (isSelected) selected.delete(option.value)
                      else selected.add(option.value)
                      const values = Array.from(selected)
                      column?.setFilterValue(values.length ? values : undefined)
                    }}
                  >
                    <div
                      className={cn(
                        "flex size-4 items-center justify-center rounded-[4px] border border-primary",
                        isSelected
                          ? "bg-primary text-primary-foreground"
                          : "opacity-50 [&_svg]:invisible",
                      )}
                    >
                      <Check className="size-3" />
                    </div>
                    {Icon && <Icon className="size-4 text-muted-foreground" />}
                    <span>{option.label}</span>
                    {/* Live count from the faceted row model. */}
                    {facets?.get(option.value) != null && (
                      <span className="ml-auto flex size-4 items-center justify-center font-mono text-xs tabular-nums">
                        {facets.get(option.value)}
                      </span>
                    )}
                  </CommandItem>
                )
              })}
            </CommandGroup>
            {selected.size > 0 && (
              <>
                <CommandSeparator />
                <CommandGroup>
                  <CommandItem
                    onSelect={() => column?.setFilterValue(undefined)}
                    className="justify-center text-center"
                  >
                    Clear filters
                  </CommandItem>
                </CommandGroup>
              </>
            )}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
```

### `data-table-toolbar.tsx` — search + facets + reset + view

```tsx
"use client"

import type { Table } from "@tanstack/react-table"
import { Settings2, X } from "lucide-react"

import { PRIORITIES, STATUSES } from "./columns"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { DataTableFacetedFilter } from "./data-table-faceted-filter"

const toOptions = (
  record: Record<string, { label: string; icon?: React.ComponentType<{ className?: string }> }>,
) =>
  Object.entries(record).map(([value, { label, icon }]) => ({ value, label, icon }))

export function DataTableToolbar<TData>({ table }: { table: Table<TData> }) {
  const isFiltered = table.getState().columnFilters.length > 0

  return (
    <div className="flex items-center justify-between gap-2">
      <div className="flex flex-1 flex-wrap items-center gap-2">
        <Input
          placeholder="Filter tasks…"
          value={(table.getColumn("title")?.getFilterValue() as string) ?? ""}
          onChange={(e) =>
            table.getColumn("title")?.setFilterValue(e.target.value)
          }
          className="h-8 w-40 lg:w-64"
          aria-label="Filter tasks by title"
        />
        {table.getColumn("status") && (
          <DataTableFacetedFilter
            column={table.getColumn("status")}
            title="Status"
            options={toOptions(STATUSES)}
          />
        )}
        {table.getColumn("priority") && (
          <DataTableFacetedFilter
            column={table.getColumn("priority")}
            title="Priority"
            options={toOptions(PRIORITIES)}
          />
        )}
        {isFiltered && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => table.resetColumnFilters()}
            className="h-8 px-2 lg:px-3"
          >
            Reset
            <X className="size-3.5" />
          </Button>
        )}
      </div>

      {/* View: column visibility. Persist this to localStorage/URL in prod. */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" className="ml-auto h-8">
            <Settings2 className="size-3.5" />
            <span className="hidden lg:inline">View</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-40">
          <DropdownMenuLabel>Toggle columns</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {table
            .getAllColumns()
            .filter((c) => c.getCanHide())
            .map((column) => (
              <DropdownMenuCheckboxItem
                key={column.id}
                className="capitalize"
                checked={column.getIsVisible()}
                onCheckedChange={(v) => column.toggleVisibility(!!v)}
              >
                {column.id}
              </DropdownMenuCheckboxItem>
            ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}
```

### `data-table-pagination.tsx` — count + rows-per-page + page controls

```tsx
"use client"

import type { Table } from "@tanstack/react-table"
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export function DataTablePagination<TData>({ table }: { table: Table<TData> }) {
  const { pageIndex, pageSize } = table.getState().pagination
  const selectedCount = table.getFilteredSelectedRowModel().rows.length
  const totalCount = table.getFilteredRowModel().rows.length

  return (
    <div className="flex flex-col-reverse items-center gap-3 px-1 sm:flex-row sm:justify-between">
      {/* Selection count — announced politely for screen readers. */}
      <div
        className="text-sm text-muted-foreground tabular-nums"
        aria-live="polite"
      >
        {selectedCount} of {totalCount} row(s) selected.
      </div>

      <div className="flex items-center gap-4 sm:gap-6">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium">Rows per page</p>
          <Select
            value={`${pageSize}`}
            onValueChange={(v) => table.setPageSize(Number(v))}
          >
            <SelectTrigger className="h-8 w-[70px]">
              <SelectValue placeholder={pageSize} />
            </SelectTrigger>
            <SelectContent side="top">
              {[10, 25, 50, 100].map((n) => (
                <SelectItem key={n} value={`${n}`}>
                  {n}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-1 text-sm font-medium tabular-nums">
          Page {pageIndex + 1} of {table.getPageCount()}
        </div>

        <div className="flex items-center gap-1">
          <Button
            variant="outline"
            size="icon"
            className="hidden size-8 lg:flex"
            onClick={() => table.setPageIndex(0)}
            disabled={!table.getCanPreviousPage()}
            aria-label="Go to first page"
          >
            <ChevronsLeft className="size-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="size-8"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            aria-label="Go to previous page"
          >
            <ChevronLeft className="size-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="size-8"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            aria-label="Go to next page"
          >
            <ChevronRight className="size-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="hidden size-8 lg:flex"
            onClick={() => table.setPageIndex(table.getPageCount() - 1)}
            disabled={!table.getCanNextPage()}
            aria-label="Go to last page"
          >
            <ChevronsRight className="size-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
```

### `data-table.tsx` — the reusable engine + shell + states

```tsx
"use client"

import * as React from "react"
import {
  type ColumnDef,
  type ColumnFiltersState,
  type SortingState,
  type VisibilityState,
  flexRender,
  getCoreRowModel,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { DataTablePagination } from "./data-table-pagination"
import { DataTableToolbar } from "./data-table-toolbar"

type Density = "compact" | "comfortable" | "spacious"

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  isLoading?: boolean
  isError?: boolean
  onRetry?: () => void
  onCreate?: () => void
  density?: Density
}

export function DataTable<TData, TValue>({
  columns,
  data,
  isLoading = false,
  isError = false,
  onRetry,
  onCreate,
  density = "compact",
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])
  const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({})
  const [rowSelection, setRowSelection] = React.useState({})

  const table = useReactTable({
    data,
    columns,
    state: { sorting, columnFilters, columnVisibility, rowSelection },
    initialState: { pagination: { pageSize: 25 } }, // research-optimal default
    enableRowSelection: true,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
  })

  const isFiltered = table.getState().columnFilters.length > 0
  const colSpan = table.getVisibleFlatColumns().length

  return (
    <div className="space-y-3" data-density={density}>
      <DataTableToolbar table={table} />

      {/* Horizontal scroll container: table never crushes columns. */}
      <div className="overflow-hidden rounded-md border">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader className="bg-muted/40">
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id} className="hover:bg-transparent">
                  {headerGroup.headers.map((header) => {
                    const sortDir = header.column.getIsSorted()
                    return (
                      <TableHead
                        key={header.id}
                        // aria-sort reflects the live sort direction.
                        aria-sort={
                          sortDir === "asc"
                            ? "ascending"
                            : sortDir === "desc"
                              ? "descending"
                              : header.column.getCanSort()
                                ? "none"
                                : undefined
                        }
                        style={{ width: header.getSize() }}
                        className="text-muted-foreground"
                      >
                        {header.isPlaceholder
                          ? null
                          : flexRender(
                              header.column.columnDef.header,
                              header.getContext(),
                            )}
                      </TableHead>
                    )
                  })}
                </TableRow>
              ))}
            </TableHeader>

            <TableBody aria-live="polite" aria-busy={isLoading}>
              {/* LOADING: skeleton the first ~5 rows, header stays live. */}
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <TableRow key={`skeleton-${i}`} className="hover:bg-transparent">
                    {table.getVisibleFlatColumns().map((col) => (
                      <TableCell
                        key={col.id}
                        style={{ paddingBlock: "var(--cell-py)" }}
                      >
                        <Skeleton className="h-4 w-full max-w-[160px]" />
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : isError ? (
                /* ERROR: inline message + retry, header preserved. */
                <TableRow className="hover:bg-transparent">
                  <TableCell colSpan={colSpan} className="h-40 text-center">
                    <div className="flex flex-col items-center gap-3">
                      <p className="text-sm text-muted-foreground">
                        There was an error loading the data.
                      </p>
                      {onRetry && (
                        <Button variant="outline" size="sm" onClick={onRetry}>
                          Retry
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ) : table.getRowModel().rows.length ? (
                table.getRowModel().rows.map((row) => (
                  <TableRow
                    key={row.id}
                    data-state={row.getIsSelected() && "selected"}
                    // group/row → children can reveal on hover; focus-within keeps
                    // keyboard users covered (never hover-only).
                    className="group/row focus-within:bg-muted/50"
                    style={{ height: "var(--row-h)" }}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <TableCell
                        key={cell.id}
                        style={{ paddingBlock: "var(--cell-py)" }}
                      >
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext(),
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : isFiltered ? (
                /* EMPTY — no results (distinct copy + clear action). */
                <TableRow className="hover:bg-transparent">
                  <TableCell colSpan={colSpan} className="h-40 text-center">
                    <div className="flex flex-col items-center gap-3">
                      <p className="text-sm text-muted-foreground">
                        No results found.
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => table.resetColumnFilters()}
                      >
                        Clear filters
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                /* EMPTY — first run (illustration/CTA). */
                <TableRow className="hover:bg-transparent">
                  <TableCell colSpan={colSpan} className="h-40 text-center">
                    <div className="flex flex-col items-center gap-3">
                      <p className="text-sm font-medium">No tasks yet</p>
                      <p className="text-sm text-muted-foreground">
                        Create your first task to get started.
                      </p>
                      {onCreate && (
                        <Button size="sm" onClick={onCreate}>
                          Create task
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      <DataTablePagination table={table} />
    </div>
  )
}
```

### `page.tsx` — server component that fetches and mounts

```tsx
import { columns } from "./columns"
import { DataTable } from "./data-table"
import type { Task } from "./types"

async function getTasks(): Promise<Task[]> {
  // Replace with your ORM/API call. Server component → data fetched on the server.
  return [
    { id: "TASK-8782", title: "Convert cross-platform interface bytes", status: "in_progress", priority: "high", estimate: 8, updatedAt: "2026-06-30" },
    { id: "TASK-7878", title: "Try to calculate the EXE feed", status: "backlog", priority: "medium", estimate: 5, updatedAt: "2026-06-29" },
    { id: "TASK-7839", title: "Bypass the neural TCP card", status: "todo", priority: "high", estimate: 13, updatedAt: "2026-06-28" },
    { id: "TASK-5562", title: "Generate the auxiliary bus", status: "done", priority: "low", estimate: 3, updatedAt: "2026-06-25" },
    // …
  ]
}

export default async function TasksPage() {
  const data = await getTasks()

  return (
    <div className="container mx-auto py-8">
      <div className="mb-4">
        <h1 className="text-xl font-semibold tracking-tight">Tasks</h1>
        <p className="text-sm text-muted-foreground">
          Manage your team's work. Sort, filter, and select in bulk.
        </p>
      </div>
      <DataTable columns={columns} data={data} density="compact" />
    </div>
  )
}
```

---

## 10. Production checklist

- [ ] Numbers right-aligned + `tabular-nums`; text left-aligned; headers match cells.
- [ ] Every hover affordance mirrored on `focus-within` / `focus-visible`.
- [ ] `aria-sort` on the active header; sort control is a real `<button>` with a label.
- [ ] Distinct **first-run** vs **no-results** empty states; **error + retry**; **skeleton (first ~5 rows, live header)** on load.
- [ ] Status/priority carry **icon + text**, not color alone.
- [ ] Checkboxes/actions have ≥24px hit areas even in compact density.
- [ ] Sort/filter/page (and, ideally, column-visibility + density) **persisted** — URL for shareable state, localStorage for prefs — with a **reset to default**.
- [ ] > 1,000 rows → server-side (Variant B) or virtualized; never client-render unbounded.
- [ ] No zebra striping; one 1px divider; no borders-everywhere; no full-table spinner; no infinite scroll.

---

## Sources

- [shadcn/ui — Data Table](https://ui.shadcn.com/docs/components/data-table) · [Table primitive](https://ui.shadcn.com/docs/components/table)
- [TanStack Table v8 — Features](https://tanstack.com/table/v8/docs/guide/features) · [Sorting](https://tanstack.com/table/v8/docs/guide/sorting) · [Column Sizing](https://tanstack.com/table/v8/docs/guide/column-sizing) · [Virtualization](https://tanstack.com/table/v8/docs/guide/virtualization) · [TanStack Virtual]
- [Pencil & Paper — Enterprise data tables UX](https://www.pencilandpaper.io/articles/ux-pattern-analysis-enterprise-data-tables)
- [Setproduct — Data table UI 2026](https://www.setproduct.com/blog/data-table-ui-design) · [Pagination UI](https://www.setproduct.com/blog/pagination-ui-design)
- [Stripe — cursor-based pagination](https://docs.stripe.com/stripe-apps/components/table) · [Linear UI patterns](https://www.saasui.design/application/linear)
- [Carbon — Loading/skeleton](https://carbondesignsystem.com/patterns/loading-pattern/) · [WCAG 2.2 — Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)

[TanStack Table v8]: https://tanstack.com/table/v8
[TanStack Virtual]: https://tanstack.com/virtual/latest
[shadcn/ui]: https://ui.shadcn.com
