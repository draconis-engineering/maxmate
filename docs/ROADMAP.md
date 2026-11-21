# Visio Roadmap

## Current state

Visio is currently a scaffold, not a chess engine. The module layout (`types`, `engine`, `math`, `exceptions`) is a reasonable foundation, but the package does not import successfully and no behavioral method is implemented. The goal of Phase 1 is a rules-complete chess game; the engine/search work starts in Phase 2.

Known blockers (see Phase 0):

- `src/visio/types.py:85-98` passes `ChessPiece` arguments in the wrong order, causing `KeyError: 'white'` on import.
- `src/visio/types.py:140` has an invalid halfmove/fullmove validation condition.
- `src/visio/types.py:207-216` returns success from `move()` without doing anything because `check_legality()` returns a truthy `Ellipsis`.
- `src/visio/types.py:231-233` `save_log()` ignores its path, uses a source file as a directory, produces the same timestamp every time, and writes nothing.
- All rules, move generation, evaluation, search, and protocol code is missing.

## Phase 0 — Make it importable and honest

Goal: the package imports, FEN parsing is trustworthy, and stubs fail loudly instead of pretending to work.

- [x] Fix `ChessPiece` constructor/call-site argument order (`types.py:72-77`, `:85-98`);
- [x] Add value semantics (`__repr__`, `__eq__`), and expose `name`, `color` and `value` -> cost?.
- [ ] Fix clock validation in `validate_fen()` (`types.py:140`) using `or` / `< 1` semantics.
- [ ] Strengthen FEN validation: exactly one king per side, no pawns on ranks 1/8, castling rights consistent with king/rook placement and order-independent, EP square rank consistent with the side to move, sane digit runs.
- [x] Make `build_board_from_fen()` validate or become private
    - [ ] document board orientation (row 0 = rank 8).
- [x] Replace `board if board else ...` with an explicit `None` check in `ChessBoard.__init__` (`types.py:192`)
    - [ ] Validate constructor state.
- [ ] Replace truthy stubs with either real implementations or explicit `NotImplementedError`
    - [ ] `check_legality()`
    - [ ] `move()`
    - [ ] `peek_algebraic()`
- [ ] Rewrite `save_log()` to use the supplied path, `datetime.now()`, a filesystem-safe filename, and actual content.
- [ ] Add algebraic<->index coordinate helpers and `to_fen()` / `__str__` for round-tripping and debugging.
- [ ] Unify color representation (`"w"/"b"` vs `"white"/"black"`) into one canonical type.
- [ ] Export exceptions and public helpers from `__init__.py`; choose one error-handling convention (raise vs `bool`).
- [x] Lower `requires-python` to `>=3.12` if no 3.14-only features are needed;
- [ ] Add README content, license metadata, and test/lint/typecheck tooling.
- [x] Stage the `projectzero` → `visio` rename so history and reviews are coherent.

Exit criteria:

- [x] `uv run python -c "import visio"` succeeds
- [ ] FEN round-trip tests pass
- [ ] no method silently reports success without doing work.

## Phase 1 — Rules-complete chess game

Goal: a fully legal, serializable game of chess with no AI yet.

- [x] Introduce a `Move` value type: from-square, to-square, promotion piece, and flags (capture, en passant, castling, double pawn push).
- [ ] Implement board coordinate helpers, square iteration, and attack maps / `is_square_attacked()`.
- [ ] Generate pseudo-legal moves for every piece; filter by own-king safety to get legal moves.
- [ ] Implement make/unmake (or copy) that updates: active color, castling rights, EP target, halfmove clock, fullmove number, captured pieces, and history stack.
- [ ] Implement special rules: castling (rights, empty squares, not through/out of check), en passant (including pinned edge cases), promotion to Q/R/B/N.
- [ ] Implement game-end detection: check, checkmate, stalemate, 50-move rule, threefold repetition, insufficient material / dead position.
- [ ] Implement SAN generation with correct disambiguation and SAN parsing against the legal move list; use UCI coordinates as the internal/default format.
- [ ] Add move history, undo, and FEN export at any point.

Exit criteria: perft numbers match for the standard test positions (see below); full games can be played to a legal conclusion with no illegal moves.

## Phase 2 — Engine core

Goal: a search that chooses legal, reasonable moves within a time budget.

- [ ] Evaluation: material from `_COSTS`, piece-square tables, mobility, pawn structure, king safety; tapered midgame/endgame scores.
- [ ] Search: negamax with alpha-beta, iterative deepening, transposition table with Zobrist hashing, move ordering (MVV-LVA, killers, history heuristic), quiescence search.
- [ ] Search extensions/pruning: null-move pruning, late-move reductions, aspiration windows, mate-score handling.
- [ ] Principal variation extraction, node counters, and time management (movetime / time+increment).
- [ ] `Engine` API: `best_move(board, limits)` returning a validated legal move with score and PV.

Exit criteria: engine plays complete legal games under a time control; no crash or illegal move across a smoke-test match; measurable nodes/second baseline recorded.

## Phase 3 — Interface, testing, and polish

Goal: usable, verifiable, and maintainable.

- [ ] UCI protocol loop: `uci`, `isready`, `ucinewgame`, `position [startpos|fen ...] moves ...`, `go`, `stop`, `quit`.
- [ ] Simple terminal board renderer for debugging and manual play.
- [ ] Test suite: unit tests for rules, perft regression tests, FEN/SAN property tests, UCI integration tests.
- [ ] CI running formatting, lint, typecheck, and tests; benchmark job tracking search performance.
- [ ] README with installation, usage, architecture overview, and contribution notes.
- [ ] Optional later: opening book, endgame tablebases, NNUE evaluation, GUI/web frontend.

## Reference perft values

| Position                                                                 | Depth 1 | Depth 2 | Depth 3 |   Depth 4 |     Depth 5 |
| ------------------------------------------------------------------------ | ------: | ------: | ------: | --------: | ----------: |
| Startpos                                                                 |      20 |     400 |   8,902 |   197,281 |   4,865,609 |
| Kiwipete (`r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R ...`) |      48 |   2,039 |  97,862 | 4,085,603 | 193,690,690 |

## Out of scope for now

NNUE, opening books, tablebases, multiprocessing, network play, and graphical interfaces. Revisit after Phase 2 exit criteria are met.
