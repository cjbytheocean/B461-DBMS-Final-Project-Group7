import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class Utils {
    public static void deleteRecursively(Path path) {
        try {
            Files.list(path).forEach(Utils::deleteRecursively);
        } catch (IOException e) {
            return;
        }
    }
}
