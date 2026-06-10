import java.util.Optional;

public record QueryModel(String kind, Optional<Integer> key, Optional<Integer> value, Optional<Integer> startKey, Optional<Integer> endKey) {}
