import type React from "react"
import { useState, useCallback, useMemo } from "react"

export interface TableData {
  [key: string]: any
}

export interface ColumnConfig {
  key: string
  header: string
  searchable?: boolean
  render?: (value: any, rowData: TableData) => React.ReactNode
  interaction?: (value: any, rowData: TableData) => void
}

interface DynamicTableProps {
  data: TableData[]
  columns: ColumnConfig[]
  className?: string
  externalSearchTerm?: string
}

const DynamicTable: React.FC<DynamicTableProps> = ({
  data,
  columns,
  className = "",
  externalSearchTerm,
}) => {
  const [internalSearchTerm, setInternalSearchTerm] = useState("")
  const [selectedRows, setSelectedRows] = useState<Set<number>>(new Set())

  const searchTerm = externalSearchTerm !== undefined ? externalSearchTerm : internalSearchTerm

  const handleInternalSearch = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setInternalSearchTerm(event.target.value)
  }, [])

  const filteredData = useMemo(() => {
    return data.filter((row) =>
      columns.some(
        (column) => column.searchable && String(row[column.key]).toLowerCase().includes(searchTerm.toLowerCase()),
      ),
    )
  }, [data, columns, searchTerm])

  const toggleRowSelection = useCallback((index: number) => {
    setSelectedRows((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(index)) {
        newSet.delete(index)
      } else {
        newSet.add(index)
      }
      return newSet
    })
  }, [])

  const toggleAllRows = useCallback(() => {
    if (selectedRows.size === filteredData.length) {
      setSelectedRows(new Set())
    } else {
      setSelectedRows(new Set(filteredData.map((_, index) => index)))
    }
  }, [filteredData, selectedRows])

  return (
    <div className={`space-y-4 ${className}`}>
      {externalSearchTerm === undefined && (
        <input
          type="text"
          placeholder="Search..."
          value={internalSearchTerm}
          onChange={handleInternalSearch}
          className="w-full p-2 border border-gray-300 rounded"
        />
      )}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <input
                  type="checkbox"
                  checked={selectedRows.size === filteredData.length && filteredData.length > 0}
                  onChange={toggleAllRows}
                  className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                />
              </th>
              {columns.map((column) => (
                <th
                  key={column.key}
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredData.map((row, rowIndex) => (
              <tr key={rowIndex} className={rowIndex % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <input
                    type="checkbox"
                    checked={selectedRows.has(rowIndex)}
                    onChange={() => toggleRowSelection(rowIndex)}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  />
                </td>
                {columns.map((column) => (
                  <td key={column.key} className="px-6 py-4 whitespace-nowrap">
                    {column.interaction ? (
                      <span
                        onClick={() => column.interaction!(row[column.key], row)}
                        className="cursor-pointer text-blue-600 hover:text-blue-800 hover:underline"
                      >
                        {column.render ? column.render(row[column.key], row) : row[column.key]}
                      </span>
                    ) : column.render ? (
                      column.render(row[column.key], row)
                    ) : (
                      row[column.key]
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="text-sm text-gray-500">
        Selected {selectedRows.size} of {filteredData.length} rows
      </div>
    </div>
  )
}

export default DynamicTable

// Example usage of the DynamicTable component with external search
export const ExampleUsage: React.FC = () => {
  const [externalSearchTerm, setExternalSearchTerm] = useState("")

  const sampleData = [
    { id: 1, name: "John Doe", age: 30, role: "Developer", website: "https://johndoe.com" },
    { id: 2, name: "Jane Smith", age: 28, role: "Designer", website: "https://janesmith.com" },
    { id: 3, name: "Bob Johnson", age: 35, role: "Manager", website: "https://bobjohnson.com" },
    { id: 4, name: "Alice Brown", age: 32, role: "Developer", website: "https://alicebrown.com" },
    { id: 5, name: "Charlie Davis", age: 40, role: "Designer", website: "https://charliedavis.com" },
  ]

  const columns: ColumnConfig[] = [
    { key: "id", header: "ID", searchable: true },
    {
      key: "name",
      header: "Name",
      searchable: true,
      interaction: (value, rowData) => {
        window.open(rowData.website, "_blank")
      },
      render: (value) => <span className="font-medium">{value}</span>,
    },
    { key: "age", header: "Age", searchable: true },
    {
      key: "role",
      header: "Role",
      searchable: true,
      render: (value) => <span className="font-semibold text-blue-600">{value}</span>,
    },
    {
      key: "actions",
      header: "Actions",
      render: (_, rowData) => (
        <button
          onClick={() => alert(`Editing user: ${rowData.name}`)}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Edit
        </button>
      ),
    },
  ]

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Enhanced Dynamic Table Example</h1>
      <div className="mb-4 flex space-x-2">
        <input
          type="text"
          placeholder="External Search..."
          value={externalSearchTerm}
          onChange={(e) => setExternalSearchTerm(e.target.value)}
          className="flex-grow p-2 border border-gray-300 rounded"
        />
        <button
          onClick={() => alert("Custom action")}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Custom Action
        </button>
      </div>
      <DynamicTable data={sampleData} columns={columns} externalSearchTerm={externalSearchTerm} />
    </div>
  )
}

