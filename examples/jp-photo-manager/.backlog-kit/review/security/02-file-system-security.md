# File System Security
Read when: a change touches file or path handling, uploads, file-serving endpoints, or thumbnail generation

## 2. File System Security (Critical for a Photo Manager)

The application reads, writes, and thumbnails arbitrary file paths supplied by
the user. This is the highest-risk attack surface in this codebase.

### 2.1 Path Traversal

🔴 Flag any file operation that uses a user-supplied path directly without
canonicalisation and containment checks. The canonical fix is:

```java
Path base = Paths.get(allowedRootDirectory).toRealPath();
Path target = base.resolve(userSuppliedRelativePath).normalize();
if (!target.startsWith(base)) {
    throw new SecurityException("Path traversal attempt: " + target);
}
```

🔴 Flag any endpoint that returns file contents (bytes, streams) when the path is
derived from a request parameter without the check above.

🔴 Flag any thumbnail URL or file URL that embeds an absolute filesystem path
exposed in an API response — callers should receive an opaque ID, not a raw path.

### 2.2 File Type Validation

🔴 Flag any file-upload or file-read path that relies **only** on the file
extension to determine content type. Magic-byte validation must also be done:

```java
// Apache Commons Imaging already does this for supported formats
// For a generic check, use Tika or Files.probeContentType()
String detectedType = tika.detect(inputStream);
if (!ALLOWED_MIME_TYPES.contains(detectedType)) {
    throw new IllegalArgumentException("Unsupported file type: " + detectedType);
}
```

🟡 Flag any code that writes a user-supplied filename directly to disk without
sanitising it (remove `..`, `/`, `\`, null bytes, and leading dots).

### 2.3 Thumbnail Generation

🟡 Flag thumbnail generation code that does not set limits on image dimensions
before decoding. Decompression bomb (e.g., a 1×1 JPEG that expands to 100 MB)
can exhaust heap. Use a library that supports dimension-before-decode checks.

🟢 Flag any temporary file created during thumbnail generation that is not
cleaned up in a `finally` block or `try-with-resources`.
