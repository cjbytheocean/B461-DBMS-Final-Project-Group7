import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Optional;

public class Main {
    public static void main(String[] args) {
        Optional<Path> dir = Optional.empty();
        try {
            dir = Optional.of(Files.createTempDirectory("dbms-"));
            // TODO: run simulation
        } catch (IOException e) {
            throw new RuntimeException(e);
        } finally {
            dir.ifPresent(Utils::deleteRecursively);
        }
    }
}
