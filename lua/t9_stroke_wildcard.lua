local M = {}

local MAX_WILDCARDS = 2
local RESULTS_PER_BRANCH = 12
local MAX_RESULTS = 120

local function expand_wildcards(input)
    local _, wildcard_count = input:gsub("6", "")
    if wildcard_count == 0 or wildcard_count > MAX_WILDCARDS then
        return nil
    end

    local variants = { "" }
    for index = 1, #input do
        local token = input:sub(index, index)
        local next_variants = {}
        if token == "6" then
            for _, prefix in ipairs(variants) do
                for stroke = 1, 5 do
                    next_variants[#next_variants + 1] = prefix .. stroke
                end
            end
        else
            for _, prefix in ipairs(variants) do
                next_variants[#next_variants + 1] = prefix .. token
            end
        end
        variants = next_variants
    end
    return variants
end

function M.init(env)
    env.stroke_exact = Component.Translator(
        env.engine,
        "translator",
        "table_translator"
    )
end

function M.fini(env)
    env.stroke_exact = nil
end

function M.func(input, segment, env)
    local variants = expand_wildcards(input)
    if variants == nil then
        return
    end

    local ranked = {}
    local by_text = {}
    local insertion_order = 0
    for _, variant in ipairs(variants) do
        local translation = env.stroke_exact:query(variant, segment)
        if translation ~= nil then
            local branch_count = 0
            for candidate in translation:iter() do
                branch_count = branch_count + 1
                if branch_count > RESULTS_PER_BRANCH then break end
                insertion_order = insertion_order + 1
                local quality = candidate.quality or 0
                local previous = by_text[candidate.text]
                if previous == nil then
                    local entry = {
                        candidate = candidate,
                        quality = quality,
                        order = insertion_order,
                    }
                    ranked[#ranked + 1] = entry
                    by_text[candidate.text] = entry
                elseif quality > previous.quality then
                    previous.candidate = candidate
                    previous.quality = quality
                end
            end
        end
    end

    table.sort(ranked, function(left, right)
        if left.quality == right.quality then
            return left.order < right.order
        end
        return left.quality > right.quality
    end)

    for index = 1, math.min(#ranked, MAX_RESULTS) do
        yield(ranked[index].candidate)
    end
end

return M
