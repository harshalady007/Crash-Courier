type CrazySDK = {
  init?: () => Promise<void> | void;
  game?: {
    gameplayStart?: () => void;
    gameplayStop?: () => void;
    loadingStart?: () => void;
    loadingStop?: () => void;
    happytime?: () => void;
  };
};
declare global {
  interface Window {
    CrazyGames?: { SDK?: CrazySDK };
  }
}
export class CrazyGamesBridge {
  private sdk?: CrazySDK;
  private initialized = false;
  async init(): Promise<void> {
    this.sdk = window.CrazyGames?.SDK;
    try {
      await this.sdk?.init?.();
      this.initialized = Boolean(this.sdk);
    } catch {
      this.initialized = false;
    }
  }
  get isAvailable(): boolean {
    return this.initialized;
  }
  gameplayStart(): void {
    this.sdk?.game?.gameplayStart?.();
  }
  gameplayStop(): void {
    this.sdk?.game?.gameplayStop?.();
  }
  loadingStart(): void {
    this.sdk?.game?.loadingStart?.();
  }
  loadingStop(): void {
    this.sdk?.game?.loadingStop?.();
  }
  happytime(): void {
    this.sdk?.game?.happytime?.();
  }
}
