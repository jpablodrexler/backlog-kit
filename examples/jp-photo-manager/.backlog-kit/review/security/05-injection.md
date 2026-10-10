# Injection Vulnerabilities
Read when: a change touches queries, native SQL, or process or shell invocation

## 5. Injection Vulnerabilities

### 5.1 SQL / JPQL Injection

🔴 Flag any `@Query` that concatenates user input into the JPQL or SQL string
instead of using named parameters:

```java
// Wrong
@Query("SELECT a FROM Asset a WHERE a.fileName = '" + fileName + "'")

// Right
@Query("SELECT a FROM Asset a WHERE a.fileName = :fileName")
List<Asset> findByFileName(@Param("fileName") String fileName);
```

🟡 Flag any `EntityManager.createNativeQuery()` call that uses string
concatenation with user input.

### 5.2 OS Command Injection

🔴 Flag any call to `Runtime.exec()`, `ProcessBuilder`, or similar that
includes a user-supplied value without shell-escape:

```java
// Wrong — user supplies folderPath
Runtime.getRuntime().exec("ls " + folderPath);

// Right — pass as separate argument, never via shell string
new ProcessBuilder("ls", folderPath).start();
```

🔴 Flag any image-processing library invocation (e.g., ImageMagick via CLI
wrapper) that interpolates user-supplied filenames into a shell command.
