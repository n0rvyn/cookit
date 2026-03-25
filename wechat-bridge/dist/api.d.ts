import type { BaseInfo, GetUpdatesReq, GetUpdatesResp, SendMessageReq, SendTypingReq, GetConfigResp } from "./types.js";
export interface WeixinApiOptions {
    baseUrl: string;
    token?: string;
    routeTag?: string;
    timeoutMs?: number;
    longPollTimeoutMs?: number;
}
export declare function buildBaseInfo(): BaseInfo;
export declare function getUpdates(params: GetUpdatesReq & WeixinApiOptions): Promise<GetUpdatesResp>;
export declare function sendMessage(params: WeixinApiOptions & {
    body: SendMessageReq;
}): Promise<void>;
export declare function getConfig(params: WeixinApiOptions & {
    ilinkUserId: string;
    contextToken?: string;
}): Promise<GetConfigResp>;
export declare function sendTyping(params: WeixinApiOptions & {
    body: SendTypingReq;
}): Promise<void>;
