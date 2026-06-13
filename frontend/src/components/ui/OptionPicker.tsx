import { useEffect, useRef, useState } from "react";

export interface PickerOption {
  value: string;
  label: string;
}

interface OptionPickerProps {
  options: PickerOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  searchable?: boolean;
  allowCustom?: boolean;
  disabled?: boolean;
  emptyHint?: string;
}

export function OptionPicker({
  options,
  value,
  onChange,
  placeholder = "Выберите…",
  searchable = true,
  allowCustom = false,
  disabled = false,
  emptyHint = "Нет совпадений",
}: OptionPickerProps) {
  const rootRef = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [filterQuery, setFilterQuery] = useState("");

  const selected = options.find((option) => option.value === value);

  useEffect(() => {
    if (allowCustom) {
      setQuery(value);
    }
  }, [allowCustom, value]);

  useEffect(() => {
    const onOutside = (event: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) {
        setOpen(false);
        setFilterQuery("");
        if (!allowCustom) {
          setQuery("");
        }
      }
    };
    document.addEventListener("mousedown", onOutside);
    return () => document.removeEventListener("mousedown", onOutside);
  }, [allowCustom]);

  const filterText = filterQuery.trim().toLowerCase();
  const filtered =
    filterText === ""
      ? options
      : options.filter((option) => option.label.toLowerCase().includes(filterText));

  const openList = () => {
    if (disabled) return;
    setOpen(true);
    setFilterQuery("");
  };

  const pick = (option: PickerOption) => {
    onChange(option.value);
    if (allowCustom) {
      setQuery(option.label);
    }
    setFilterQuery("");
    setOpen(false);
  };

  const inputValue = allowCustom
    ? query
    : open && searchable
      ? filterQuery || selected?.label || ""
      : selected?.label ?? "";

  return (
    <div
      className={`option-picker${disabled ? " is-disabled" : ""}`}
      ref={rootRef}
    >
      <div className="option-picker-field">
        <input
          value={inputValue}
          placeholder={placeholder}
          readOnly={!searchable && !allowCustom}
          disabled={disabled}
          onChange={(event) => {
            if (disabled) return;
            const next = event.target.value;
            setOpen(true);
            if (allowCustom) {
              setQuery(next);
              setFilterQuery(next);
              onChange(next);
            } else if (searchable) {
              setFilterQuery(next);
            }
          }}
          onFocus={openList}
          onClick={openList}
        />
        <span className="option-picker-chevron" aria-hidden="true">
          ▾
        </span>
      </div>
      {open && !disabled && (
        <ul className="option-picker-dropdown" role="listbox">
          {filtered.length === 0 && (
            <li className="option-picker-empty">{emptyHint}</li>
          )}
          {filtered.map((option) => (
            <li key={option.value}>
              <button
                type="button"
                className={option.value === value ? "is-selected" : ""}
                onClick={() => pick(option)}
              >
                {option.label}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
