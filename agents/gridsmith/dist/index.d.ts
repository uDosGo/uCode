import { Grid, Cell } from '@udos/gridcore';
export { Grid } from '@udos/gridcore';

declare function importBasicProgram(programOrPath: string, worldName: string): Promise<{
    world: Record<string, unknown>;
    files: Record<string, string>;
    summary: Record<string, unknown>;
}>;

interface AmosImportResult {
    world: Record<string, unknown>;
    files: Record<string, string>;
    summary: Record<string, unknown>;
}
declare function importAmosProgram(programOrPath: string, worldName: string): Promise<AmosImportResult>;

interface CellPayload {
    char?: string;
    fg?: number;
    bg?: number;
    [key: string]: unknown;
}
declare function editCell(grid: Grid, x: number, y: number, layer: number, data: CellPayload): {
    cell: Record<string, unknown>;
    previous: Record<string, unknown> | null;
};

interface LayerSummary {
    z: number;
    cellCount: number;
}
declare function composeGridLayers(grid: Grid, layerIndices: number[]): {
    layers: LayerSummary[];
    composed: Cell[];
    cellCount: number;
};

declare function exportUvox(grid: Grid, gridId: string, outputPath: string): Promise<{
    path: string;
    bytes: number;
    cellCount: number;
}>;

interface PathNode {
    x: number;
    y: number;
    layer: number;
}
interface PathResult {
    path: PathNode[];
    steps: number;
    found: boolean;
}
declare function findPath(grid: Grid, startX: number, startY: number, endX: number, endY: number, layer?: number): PathResult;

interface WorldManifest {
    id: string;
    name: string;
    type: 'earth' | 'dungeon' | 'vault' | 'library';
    seed?: number;
    source?: 'generated' | 'basic' | 'amos';
}
declare function createWorldManifest(id: string, name: string, type: WorldManifest['type'], seed?: number, source?: WorldManifest['source']): WorldManifest;
interface WorldCreationOptions {
    name: string;
    type: WorldManifest['type'];
    cols?: number;
    rows?: number;
    seed?: number;
    terrain?: Record<string, string>;
}
declare function createWorld(options: WorldCreationOptions): Promise<{
    manifest: WorldManifest;
    grid: {
        cols: number;
        rows: number;
        cellCount: number;
    };
    files: Record<string, string>;
}>;

interface SourceMinerInput {
    source: {
        type: 'repository' | 'local_path';
        url: string;
        branch?: string;
        language: string[];
    };
    options: {
        scan_depth?: 'shallow' | 'full';
        target_patterns?: string[];
        exclude_patterns?: string[];
    };
}
interface MemoryMapEntry {
    label: string;
    address: string;
    type: string;
    description: string;
    confidence: number;
    length?: number;
    element_type?: string;
}
interface FunctionEntry {
    name: string;
    address: string;
    description: string;
    parameters: {
        register?: string;
        description: string;
    }[];
}
interface DataStructure {
    name: string;
    size: number;
    fields: {
        offset: number;
        name: string;
        size: number;
    }[];
}
interface AssetReference {
    path: string;
    type: string;
    count?: number;
    description: string;
}
interface Recommendation {
    action: string;
    target: string;
    priority: 'high' | 'medium' | 'low';
    rationale: string;
}
interface SourceMinerOutput {
    skill: 'Source-Miner';
    version: '1.0';
    executed_at: string;
    source: string;
    findings: {
        memory_map: MemoryMapEntry[];
        functions: FunctionEntry[];
        data_structures: DataStructure[];
        asset_references: AssetReference[];
    };
    recommendations: Recommendation[];
}
declare function sourceMiner(input: SourceMinerInput): SourceMinerOutput;

interface LensCraftInput {
    source_miner_report: {
        findings: {
            memory_map: Array<{
                label: string;
                address: string;
                type: string;
                description: string;
                confidence: number;
                length?: number;
            }>;
            functions: Array<{
                name: string;
                address: string;
                description: string;
            }>;
        };
        source: string;
    };
    emulator: {
        type: string;
        memory_size?: number;
        memory_base?: string;
        endianness: 'little' | 'big';
    };
    output: {
        language: string;
        module_name: string;
        path?: string;
    };
}
interface ExtractorDefinition {
    name: string;
    type: 'bitmask' | 'struct' | 'array' | 'uint8' | 'uint16' | 'uint32' | 'int16' | 'int32';
    address: string;
    size: number;
    labels?: Record<string, string>;
    fields?: Array<{
        name: string;
        offset: number;
        type: string;
        description: string;
    }>;
    element_type?: string;
    description: string;
}
interface LensCraftOutput {
    skill: 'LENS-Craft';
    version: '1.0';
    executed_at: string;
    module_path: string;
    extractors: ExtractorDefinition[];
    generated_code?: string;
    written_to?: string;
}
declare function lensCraft(input: LensCraftInput): LensCraftOutput;

interface SkinWeaverInput {
    source_assets: Array<{
        path: string;
        type: string;
        format?: string;
        transform?: {
            scale?: number;
            rotation?: number;
            center?: [number, number];
        };
    }>;
    target: {
        locale: string;
        resolution: {
            cols: number;
            rows: number;
        };
        palette: string;
    };
}
interface CharacterMapping {
    source: string;
    target_char: string;
    target_fg: number;
    target_bg: number;
    description: string;
}
interface TeletextOverride {
    header_row?: {
        fg: number;
        bg: number;
        bold?: boolean;
    };
    hud_row?: {
        fg: number;
        bg: number;
        bold?: boolean;
    };
    alert_row?: {
        fg: number;
        bg: number;
        bold?: boolean;
    };
}
interface SkinManifest {
    name: string;
    version: string;
    palette: Record<string, string>;
    character_mappings: CharacterMapping[];
    teletext_overrides: TeletextOverride;
}
interface ExportedAsset {
    source: string;
    output: string;
}
interface SkinWeaverOutput {
    skill: 'SKIN-Weaver';
    version: '1.0';
    executed_at: string;
    skin_name: string;
    manifest: SkinManifest;
    exported_assets: ExportedAsset[];
    manifest_written_to?: string;
}
declare function skinWeaver(input: SkinWeaverInput): SkinWeaverOutput;
declare function writeSkinManifest(output: SkinWeaverOutput, outputDir: string, format?: 'yaml' | 'json'): string;

interface McpScribeInput {
    program_name: string;
    program_type: 'adapt-source' | 'rewrite' | 'port-c-to-basic' | 'rewrite_inspired_by';
    game_mechanics: {
        genre: string[];
        save_system?: string;
        input_method?: string;
        persistence?: string;
    };
    source_miner_report: {
        findings: {
            memory_map: Array<{
                label: string;
                address: string;
                type: string;
                description: string;
                confidence: number;
            }>;
            functions: Array<{
                name: string;
                address: string;
                description: string;
                parameters?: Array<{
                    register?: string;
                    description: string;
                }>;
            }>;
        };
    };
}
interface McpCommand {
    name: string;
    description: string;
    parameters: Record<string, {
        type: string;
        description: string;
        default?: string;
    }>;
    action: 'lens_capture' | 'lens_restore' | 'mcp_inject' | 'emulator_control' | 'lens_query';
    payload: Record<string, unknown>;
}
interface McpScribeOutput {
    skill: 'MCP-Scribe';
    version: '1.0';
    executed_at: string;
    program: string;
    commands: McpCommand[];
}
declare function mcpScribe(input: McpScribeInput): McpScribeOutput;

interface GridSmithToolParameter {
    type: 'string' | 'number' | 'array' | 'object';
    description: string;
    default?: string | number | number[];
    items?: {
        type: 'number';
    };
}
interface GridSmithToolDefinition {
    name: string;
    description: string;
    parameters: Record<string, GridSmithToolParameter>;
}
declare const GRIDSMITH_TOOLS: GridSmithToolDefinition[];
declare function createGridWorld(cols?: number, rows?: number): {
    grid: Grid;
    cols: number;
    rows: number;
    cellCount: number;
};
declare function convertLatLonToUCode(lat: number, lon: number, level?: number): string;
declare function convertUCodeToLatLon(coord: string): {
    lat: number;
    lon: number;
} | null;

export { type AssetReference, type CellPayload, type CharacterMapping, type DataStructure, type ExtractorDefinition, type FunctionEntry, GRIDSMITH_TOOLS, type GridSmithToolDefinition, type GridSmithToolParameter, type LensCraftInput, type LensCraftOutput, type McpCommand, type McpScribeInput, type McpScribeOutput, type MemoryMapEntry, type Recommendation, type SkinManifest, type SkinWeaverInput, type SkinWeaverOutput, type SourceMinerInput, type SourceMinerOutput, type WorldCreationOptions, composeGridLayers, convertLatLonToUCode, convertUCodeToLatLon, createGridWorld, createWorld, createWorldManifest, editCell, exportUvox, findPath, importAmosProgram, importBasicProgram, lensCraft, mcpScribe, skinWeaver, sourceMiner, writeSkinManifest };
