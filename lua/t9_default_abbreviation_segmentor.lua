local M = {}

-- These are the primary prism's dictionary-backed numeric spellings after its
-- fuzzy derives. The schema contract rebuilds this set from the dictionaries so
-- a vocabulary or algebra change cannot silently divert valid Pinyin here.
local FULL_PINYIN_CODES = [[
2 3 6 22 23 24 26 28 32 33 34 36 37 38 42 43 46 48 52 53
54 56 58 62 63 64 66 68 72 73 74 76 78 82 83 84 86 88 92 93
94 96 98 224 226 234 236 242 243 244 246 248 262 264 266 268 284 286 324 326
334 336 342 343 346 348 362 364 366 368 384 386 424 426 434 436 462 466 468 482
484 486 524 526 534 536 542 543 546 548 562 566 568 582 583 584 586 624 626 634
636 642 643 646 648 662 666 668 683 686 724 726 734 736 742 743 744 746 748 762
766 768 782 783 784 786 824 826 834 843 862 866 868 884 886 924 926 934 936 942
943 944 946 948 962 966 968 983 984 986 2246 2264 2286 2346 2364 2424 2426 2436 2446 2462
2464 2466 2468 2482 2484 2486 2646 2664 2826 2834 2836 3246 3264 3286 3346 3364 3426 3446 3462 3464
3468 3646 3664 3826 3834 3836 4246 4264 4286 4346 4364 4646 4664 4824 4826 4834 4836 5246 5264 5286
5346 5364 5426 5446 5462 5464 5466 5468 5646 5664 5824 5826 5834 5836 6246 6264 6286 6346 6364 6426
6446 6462 6464 6468 6646 6664 6826 7246 7264 7286 7346 7364 7424 7426 7434 7436 7446 7462 7464
7466 7468 7482 7484 7486 7646 7664 7826 7834 7836 8246 8264 8286 8346 8364 8426 8446 8462 8464 8646
8664 8826 8834 8836 9246 9264 9286 9346 9364 9424 9426 9434 9436 9446 9462 9464 9466 9468 9482 9484
9486 9646 9664 9826 9834 9836 22464 24246 24264 24286 24346 24364 24646 24664 24824 24826 24834 24836 42864 48246
48264 52464 52864 54246 54264 54646 54664 58246 58264 62464 64246 64264 72464 74246 74264 74286 74346 74364 74646 74664
74824 74826 74834 74836 92464 94246 94264 94286 94346 94364 94646 94664 94824 94826 94834 94836 242864 248246 248264 742864
748246 748264 942864 948246 948264
]]

local root = {}

for code in FULL_PINYIN_CODES:gmatch("%d+") do
    local node = root
    for index = 1, #code do
        local digit = code:sub(index, index)
        node[digit] = node[digit] or {}
        node = node[digit]
    end
    node.terminal = true
end

local function advance(states, digit)
    local next_states = {}
    for node in pairs(states) do
        local child = node[digit]
        if child ~= nil then
            next_states[child] = true
            if child.terminal then
                next_states[root] = true
            end
        end
    end
    return next_states
end

local function is_empty(states)
    return next(states) == nil
end

local function can_continue_as_full_pinyin(input, env)
    if input == env.last_input then return env.last_valid end

    local states
    local next_index
    if env.last_input ~= nil
        and #input == #env.last_input + 1
        and input:sub(1, #env.last_input) == env.last_input
    then
        if not env.last_valid then
            env.last_input = input
            return false
        end
        states = env.last_states
        next_index = #input
    else
        states = { [root] = true }
        next_index = 1
    end

    for index = next_index, #input do
        states = advance(states, input:sub(index, index))
        if is_empty(states) then
            env.last_input = input
            env.last_states = nil
            env.last_valid = false
            return false
        end
    end
    env.last_input = input
    env.last_states = states
    env.last_valid = true
    return true
end

function M.init(env)
    env.last_input = nil
    env.last_states = nil
    env.last_valid = nil
end

function M.func(segmentation, env)
    local start = segmentation:get_current_start_position()
    local input = segmentation.input:sub(start + 1)
    if input == "" or not input:match("^[2-9]+$") then
        M.init(env)
        return true
    end
    if can_continue_as_full_pinyin(input, env) then
        return true
    end

    -- An impossible full-Pinyin prefix is monotonic until the user deletes it.
    -- Route that segment exclusively so normal numeric Pinyin pays no second dictionary query.
    local segment = Segment(start, #segmentation.input)
    segment.tags = Set({ "abc", "t9_default_abbreviation" })
    segmentation:add_segment(segment)
    return false
end

return M
