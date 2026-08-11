import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { sendChat } from "../api";

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  route?: string;
}

export default function Chat() {
  const [input, setInput] = useState("");
  const [route, setRoute] = useState<"ODA" | "Hybrid" | "Cloud">("Hybrid");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = {
      id: `${Date.now()}-user`,
      content: input.trim(),
      role: "user",
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await sendChat(input.trim(), route);
      const botMsg: Message = {
        id: `${Date.now()}-bot`,
        content: response.final_output,
        role: "assistant",
        route: response.route,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errMsg: Message = {
        id: `${Date.now()}-err`,
        content: "Failed to get response. Please try again.",
        role: "assistant",
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  const renderItem = ({ item }: { item: Message }) => (
    <View style={[styles.message, item.role === "user" ? styles.userMsg : styles.botMsg]}>
      <Text style={styles.messageText}>{item.content}</Text>
      {item.route && <Text style={styles.routeText}>Route: {item.route}</Text>}
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.routeSelector}>
        {(["ODA", "Hybrid", "Cloud"] as const).map((r) => (
          <TouchableOpacity
            key={r}
            style={[styles.routeButton, route === r && styles.routeActive]}
            onPress={() => setRoute(r)}
          >
            <Text style={[styles.routeLabel, route === r && styles.routeLabelActive]}>
              {r}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <FlatList
        data={messages}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        style={styles.messageList}
        contentContainerStyle={styles.messageListContent}
      />

      {loading && <ActivityIndicator size="small" color="#4cc9f0" />}

      <View style={styles.inputBar}>
        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="Type a message..."
          placeholderTextColor="#64748b"
          multiline
        />
        <TouchableOpacity style={styles.sendButton} onPress={handleSend} disabled={loading}>
          <Text style={styles.sendLabel}>Send</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f172a" },
  routeSelector: {
    flexDirection: "row",
    justifyContent: "center",
    gap: 8,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#334155",
  },
  routeButton: {
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: "#1e293b",
  },
  routeActive: { backgroundColor: "#4cc9f0" },
  routeLabel: { color: "#94a3b8" },
  routeLabelActive: { color: "#fff", fontWeight: "600" },
  messageList: { flex: 1 },
  messageListContent: { padding: 16, gap: 8 },
  message: {
    maxWidth: "80%",
    padding: 12,
    borderRadius: 12,
  },
  userMsg: { alignSelf: "flex-end", backgroundColor: "#4cc9f0" },
  botMsg: { alignSelf: "flex-start", backgroundColor: "#1e293b" },
  messageText: { color: "#e2e8f0", fontSize: 15, lineHeight: 20 },
  routeText: { color: "#94a3b8", fontSize: 12, marginTop: 4 },
  inputBar: {
    flexDirection: "row",
    alignItems: "flex-end",
    padding: 12,
    gap: 8,
    borderTopWidth: 1,
    borderTopColor: "#334155",
  },
  input: {
    flex: 1,
    backgroundColor: "#1e293b",
    color: "#e2e8f0",
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    maxHeight: 100,
  },
  sendButton: {
    backgroundColor: "#4cc9f0",
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  sendLabel: { color: "#fff", fontWeight: "600" },
});