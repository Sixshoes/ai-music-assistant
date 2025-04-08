export class Logger {
  static info(message: string): void {
    console.log(`[INFO] ${message}`);
  }

  static error(message: string, error?: Error): void {
    console.error(`[ERROR] ${message}`, error);
  }

  static warn(message: string): void {
    console.warn(`[WARN] ${message}`);
  }

  static debug(message: string): void {
    if (process.env.NODE_ENV === 'development') {
      console.debug(`[DEBUG] ${message}`);
    }
  }
} 