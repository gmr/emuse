import { BellIcon } from "@heroicons/react/24/outline";

export default function Notifications() {
  return (
    <button
      type="button"
      className="relative rounded-full bg-rose-950 p-1 text-gray-400 hover:text-white focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800 focus:outline-hidden"
    >
      <span className="absolute -inset-1.5" />
      <span className="sr-only">View notifications</span>
      <BellIcon aria-hidden="true" className="size-6" />
    </button>
  );
}
