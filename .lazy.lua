local adapter = require("neotest-playwright.types.adapter")

-- Busca playwright.config.ts subiendo desde el cwd de nvim hasta la raiz del
-- proyecto (o un limite). Devuelve el directorio que lo contiene.
local function find_frontend_dir()
  local dir = vim.loop.cwd()
  local guard = 0
  while dir and dir ~= "/" and guard < 10 do
    if vim.uv.fs_stat(dir .. "/playwright.config.ts") then
      return dir
    end
    local parent = vim.fn.fnamemodify(dir, ":h")
    if parent == dir then
      break
    end
    dir = parent
    guard = guard + 1
  end
  -- Fallback: si nvim esta en la raiz del repo, el frontend esta en src/frontend.
  local cwd = vim.loop.cwd()
  if vim.uv.fs_stat(cwd .. "/src/frontend/playwright.config.ts") then
    return cwd .. "/src/frontend"
  end
  error("playwright.config.ts no encontrado a partir de " .. vim.loop.cwd())
end

return {
  {
    "nvim-neotest/neotest",
    dependencies = {
      "nvim-neotest/nvim-nio",
      "nvim-lua/plenary.nvim",
      "antoinemadec/FixCursorHold.nvim",
      "nvim-treesitter/nvim-treesitter",
      { "thenbe/neotest-playwright", dependencies = "nvim-telescope/telescope.nvim" },
    },
    config = function()
      require("neotest").setup({
        -- La config global (plugins/neotest.lua) deshabilita discovery. Lo
        -- re-habilitamos para que neotest detecte los specs E2E de este repo.
        discovery = {
          enabled = true,
        },
        adapters = {
          require("neotest-playwright").adapter({
            options = {
              persist_project_selection = true,
              enable_dynamic_test_discovery = true,
              preset = "none", -- "none" | "headed" | "debug"
              env = {
                NODE_ENV = "test",
                -- TZ = "UTC",
              },
              -- El frontend (playwright.config.ts + node_modules) vive en
              -- src/frontend/. El finder por defecto de neotest-playwright
              -- busca <cwd>/node_modules/.bin/playwright y
              -- <cwd>/playwright.config.ts, que no existen si nvim se abre en
              -- la raiz del repo. Se resuelve buscando el config y usando su
              -- directorio para el binario.
              get_playwright_config = function()
                return find_frontend_dir() .. "/playwright.config.ts"
              end,
              get_playwright_binary = function()
                return find_frontend_dir() .. "/node_modules/.bin/playwright"
              end,
              is_test_file = function(file_path)
                -- Solo specs E2E de Playwright (*.spec.ts), excluyendo unit.
                -- Los *.ct.spec.tsx (CT) y *.test.tsx (Vitest) no son de este
                -- adapter.
                return file_path:find("%.spec%.ts$") ~= nil
                  and not file_path:find("tests/unit")
              end,
            },
          }),
        },
      })
    end,
  },
}
