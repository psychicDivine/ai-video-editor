/**
 * Video Metadata Extraction Utilities
 * Extracts duration, resolution, and generates thumbnail filmstrips
 */

export interface VideoMetadata {
    duration: number;
    width: number;
    height: number;
    aspectRatio: string;
    thumbnails: string[];
}

/**
 * Extract metadata from a video file
 */
export async function extractVideoMetadata(
    file: File,
    thumbnailCount: number = 5
): Promise<VideoMetadata> {
    return new Promise((resolve, reject) => {
        const video = document.createElement('video');
        const url = URL.createObjectURL(file);
        
        video.preload = 'metadata';
        video.muted = true;
        video.src = url;
        
        video.onloadedmetadata = async () => {
            const duration = video.duration;
            const width = video.videoWidth;
            const height = video.videoHeight;
            
            // Calculate aspect ratio
            const gcd = (a: number, b: number): number => b === 0 ? a : gcd(b, a % b);
            const divisor = gcd(width, height);
            const aspectRatio = `${width / divisor}:${height / divisor}`;
            
            // Generate thumbnails
            let thumbnails: string[] = [];
            try {
                thumbnails = await generateThumbnails(video, duration, thumbnailCount);
            } catch (e) {
                console.warn('Thumbnail generation failed:', e);
            }
            
            URL.revokeObjectURL(url);
            
            resolve({
                duration,
                width,
                height,
                aspectRatio,
                thumbnails
            });
        };
        
        video.onerror = () => {
            URL.revokeObjectURL(url);
            reject(new Error('Failed to load video metadata'));
        };
    });
}

/**
 * Generate thumbnail images at intervals throughout the video
 */
async function generateThumbnails(
    video: HTMLVideoElement,
    duration: number,
    count: number
): Promise<string[]> {
    const thumbnails: string[] = [];
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    if (!ctx) return thumbnails;
    
    // Thumbnail dimensions (small for filmstrip)
    const thumbHeight = 40;
    const thumbWidth = Math.round((video.videoWidth / video.videoHeight) * thumbHeight);
    canvas.width = thumbWidth;
    canvas.height = thumbHeight;
    
    const interval = duration / (count + 1);
    
    for (let i = 1; i <= count; i++) {
        const time = interval * i;
        try {
            await seekToTime(video, time);
            ctx.drawImage(video, 0, 0, thumbWidth, thumbHeight);
            thumbnails.push(canvas.toDataURL('image/jpeg', 0.6));
        } catch (e) {
            // Skip failed thumbnails
        }
    }
    
    return thumbnails;
}

/**
 * Seek video to specific time and wait for it to be ready
 */
function seekToTime(video: HTMLVideoElement, time: number): Promise<void> {
    return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error('Seek timeout')), 3000);
        
        video.onseeked = () => {
            clearTimeout(timeout);
            resolve();
        };
        
        video.onerror = () => {
            clearTimeout(timeout);
            reject(new Error('Seek error'));
        };
        
        video.currentTime = time;
    });
}

/**
 * Format duration to MM:SS or HH:MM:SS
 */
export function formatDuration(seconds: number): string {
    if (!isFinite(seconds) || seconds < 0) return '0:00';
    
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hrs > 0) {
        return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Format resolution to common name
 */
export function formatResolution(_width: number, height: number): string {
    if (height >= 2160) return '4K';
    if (height >= 1440) return '2K';
    if (height >= 1080) return '1080p';
    if (height >= 720) return '720p';
    if (height >= 480) return '480p';
    return `${height}p`;
}
