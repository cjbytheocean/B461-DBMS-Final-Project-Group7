import java.util.Arrays;

public record PageModel(int pageId, byte[] data, int pinCount, boolean isDirty) {
    public byte[] copyBytes() {
        return Arrays.copyOf(data, data.length);
    }

    static byte[] fromSize() {
        return new byte[Config.PAGE_SIZE];
    }
}